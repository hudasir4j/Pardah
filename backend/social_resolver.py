"""
Resolve social-media crawler URLs to the real CDN image URL.

Background:
Bing/Google frequently return Instagram & Facebook "crawler" URLs that are
actually HTML pages designed for search-engine previews (e.g.
`https://lookaside.instagram.com/seo/google_widget/crawler/?media_id=...`).
PIL correctly refuses to open them as images. The real image URL is inside
the HTML as an `<meta property="og:image">` tag.

This module:
- Detects those URLs.
- Upgrades them to the real CDN URL by fetching the HTML (with a browser UA +
  appropriate Referer) and parsing og:image.
- Falls back to the same og:image behavior for any generic page URL.
"""
from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlsplit

from http_client import fetch_bytes


# Instagram's lookaside crawler endpoint only serves the SEO page (with the
# og:image we need) to known search-engine bots. A real-browser UA gets the
# fully-client-rendered app shell instead, which has no og:image.
_GOOGLEBOT_UA = (
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
)


def _crawler_user_agent(url: str) -> Optional[str]:
    host = (urlsplit(url).hostname or "").lower()
    if "lookaside" in host:
        return _GOOGLEBOT_UA
    return None


_OG_IMAGE_RE = re.compile(
    r"""<meta\s+[^>]*property\s*=\s*["']og:image(?::secure_url)?["'][^>]*content\s*=\s*["']([^"']+)["']""",
    re.IGNORECASE | re.DOTALL,
)
_OG_IMAGE_RE_REVERSED = re.compile(
    r"""<meta\s+[^>]*content\s*=\s*["']([^"']+)["'][^>]*property\s*=\s*["']og:image(?::secure_url)?["']""",
    re.IGNORECASE | re.DOTALL,
)


def is_social_crawler_url(url: str) -> bool:
    """Known HTML-landing URLs that look like images but aren't."""
    if not url:
        return False
    if "lookaside.instagram.com/seo/google_widget/crawler" in url:
        return True
    if "lookaside.fbsbx.com/lookaside/crawler/instagram/" in url:
        return True
    if "lookaside.fbsbx.com/lookaside/crawler/media/" in url:
        return True
    return False


def _extract_og_image(html: bytes) -> Optional[str]:
    try:
        text = html.decode("utf-8", errors="replace")
    except Exception:
        return None
    m = _OG_IMAGE_RE.search(text) or _OG_IMAGE_RE_REVERSED.search(text)
    if not m:
        return None
    og = m.group(1).strip()
    # Decode common HTML entities we actually encounter
    og = (
        og.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#x2F;", "/")
        .replace("&#47;", "/")
    )
    return og or None


def _referer_for(url: str) -> Optional[str]:
    host = (urlsplit(url).hostname or "").lower()
    if "instagram" in host:
        return "https://www.instagram.com/"
    if "fbsbx" in host or "facebook" in host:
        return "https://www.facebook.com/"
    return None


def resolve_to_image_url(url: str) -> Optional[str]:
    """
    If `url` is a known crawler landing page (or returns HTML), fetch it and
    return the og:image URL. Otherwise return None.
    """
    if not url:
        return None
    result = fetch_bytes(
        url,
        referer=_referer_for(url),
        allow_html=True,
        user_agent=_crawler_user_agent(url),
    )
    if not result:
        return None
    body, content_type = result
    if content_type.startswith("image/"):
        # Already an image; nothing to resolve.
        return url
    if "html" not in content_type:
        return None
    return _extract_og_image(body)


def fetch_image_bytes_with_resolve(url: str) -> Optional[bytes]:
    """
    High-level helper: return image bytes for `url`, resolving social crawler
    URLs (or any HTML response) to their og:image first.

    Returns None on permanent failure (404, 403, private content, etc.).
    """
    if not url:
        return None

    # Fast path: try to grab as an image directly.
    if not is_social_crawler_url(url):
        first = fetch_bytes(url, allow_html=True)
        if first is None:
            return None
        body, content_type = first
        if content_type.startswith("image/"):
            return body
        # HTML fallback - try og:image
        og = _extract_og_image(body)
        if not og:
            return None
        second = fetch_bytes(og, referer=_referer_for(og))
        if second is None:
            return None
        body2, ct2 = second
        return body2 if ct2.startswith("image/") else None

    # Known crawler URL: skip the wasted image fetch and go straight to HTML
    # with a crawler User-Agent (Instagram otherwise serves the client shell).
    html_resp = fetch_bytes(
        url,
        referer=_referer_for(url),
        allow_html=True,
        user_agent=_crawler_user_agent(url),
    )
    if html_resp is None:
        return None
    html_body, ct = html_resp
    if ct.startswith("image/"):
        return html_body
    og = _extract_og_image(html_body)
    if not og:
        return None
    final = fetch_bytes(og, referer=_referer_for(og))
    if final is None:
        return None
    body3, ct3 = final
    return body3 if ct3.startswith("image/") else None
