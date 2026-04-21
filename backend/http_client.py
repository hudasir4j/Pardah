"""
Shared HTTP client for image fetching.

Motivation: many image hosts (LinkedIn CDN, Evie, Instagram CDN, etc.) reject
requests whose User-Agent looks like Python/urllib. A single configured
`requests.Session` with a modern Chrome UA fixes the majority of 403s we saw
in production, and lets us layer on retries + content-type filtering.
"""
from __future__ import annotations

import time
from typing import Optional, Tuple
from urllib.parse import urlsplit

import requests


CHROME_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": CHROME_UA,
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    # Intentionally omit "br" - requests only auto-decodes gzip/deflate
    # without the optional `brotli` package. Advertising br then getting a
    # brotli-encoded body back would mean garbled responses for Bing etc.
    "Accept-Encoding": "gzip, deflate",
}

# (connect, read) seconds
DEFAULT_TIMEOUT: Tuple[float, float] = (6.0, 10.0)

# Responses larger than this are almost certainly not a personal photo and
# slow down embedding with no benefit. 20 MB is generous.
MAX_RESPONSE_BYTES = 20 * 1024 * 1024


_session: Optional[requests.Session] = None


def get_session() -> requests.Session:
    global _session
    if _session is None:
        s = requests.Session()
        s.headers.update(DEFAULT_HEADERS)
        _session = s
    return _session


def _infer_referer(url: str) -> Optional[str]:
    """Pick a sensible Referer so picky CDNs serve the asset."""
    try:
        host = urlsplit(url).hostname or ""
    except Exception:
        return None
    if host.endswith("cdninstagram.com") or "instagram.com" in host:
        return "https://www.instagram.com/"
    if "fbcdn.net" in host or "fbsbx.com" in host or "facebook.com" in host:
        return "https://www.facebook.com/"
    if "licdn.com" in host or "linkedin.com" in host:
        return "https://www.linkedin.com/"
    if "twimg.com" in host or "twitter.com" in host or host.endswith("x.com"):
        return "https://twitter.com/"
    if "tiktokcdn" in host or "tiktok.com" in host:
        return "https://www.tiktok.com/"
    return None


def fetch_bytes(
    url: str,
    *,
    referer: Optional[str] = None,
    allow_html: bool = False,
    max_retries: int = 2,
    user_agent: Optional[str] = None,
) -> Optional[Tuple[bytes, str]]:
    """
    Download a URL and return `(bytes, content_type)`.

    - Adds a Referer header automatically for known picky CDNs.
    - Retries with backoff on transient network errors and 429/5xx responses.
    - By default, rejects non-image content types. Set `allow_html=True` when
      the caller (e.g. the social resolver) wants to parse an HTML landing
      page for an og:image tag.
    - `user_agent` overrides the session default; useful when sites only
      serve SEO-friendly HTML to known search-engine crawlers.
    - Returns `None` on permanent failure (404, 403 after retries, wrong
      content type, oversized response).
    """
    session = get_session()
    headers = {}
    if user_agent:
        headers["User-Agent"] = user_agent
    ref = referer or _infer_referer(url)
    if ref:
        headers["Referer"] = ref

    last_error: Optional[str] = None
    for attempt in range(max_retries + 1):
        try:
            resp = session.get(
                url,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
                stream=True,
                allow_redirects=True,
            )
        except requests.RequestException as e:
            last_error = f"network: {e}"
            if attempt < max_retries:
                time.sleep(0.4 * (attempt + 1))
                continue
            break

        # Retry on transient server errors and rate limits
        if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
            resp.close()
            time.sleep(0.6 * (attempt + 1))
            continue

        if resp.status_code != 200:
            last_error = f"http {resp.status_code}"
            resp.close()
            break

        content_type = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        is_image = content_type.startswith("image/")
        is_html = content_type in ("text/html", "application/xhtml+xml")

        if not is_image and not (allow_html and is_html):
            last_error = f"unexpected content-type: {content_type or '<none>'}"
            resp.close()
            break

        # Guard against huge responses
        try:
            body = resp.raw.read(MAX_RESPONSE_BYTES + 1, decode_content=True)
        except Exception as e:
            last_error = f"read: {e}"
            resp.close()
            break
        finally:
            resp.close()

        if len(body) > MAX_RESPONSE_BYTES:
            return None
        return body, content_type

    if last_error:
        # Keep the log quiet; callers decide whether to print.
        pass
    return None
