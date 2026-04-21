"""
Discover the real contact email for a website.

Why: previously we just guessed `privacy@<host>`, which is right for ~30% of
small sites but wrong for newsrooms (Tracy Press uses `tpnews@tracypress.com`,
not `privacy@ttownmedia.com`). This module fetches the homepage + likely
contact pages in parallel, extracts every email it can find (mailto links,
visible text, and common obfuscations like "foo [at] bar [dot] com"), and
ranks candidates so the most-useful inbox bubbles to the top.

Optional: set `HUNTER_API_KEY` in the environment to additionally query
Hunter.io's domain-search endpoint as a fallback. We don't depend on it -
the heuristic scraper handles the long tail of small/local sites that
publish a real inbox on `/contact`.
"""
from __future__ import annotations

import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import Iterable, List, Optional, Tuple

import requests

from http_client import CHROME_UA


# Most likely paths first - we short-circuit as soon as we get a confident
# answer (mailto: + contact-page + keyword match), so order matters.
_CONTACT_PATHS = [
    "/contact",
    "/contact-us",
    "/contact/",
    "/contact-us/",
    "/contact.html",
    "/contact-us.html",
    "/about",
    "/about-us",
    "/about/",
    "/staff",
    "/team",
    "/masthead",   # newsroom convention
    "/",           # homepage footer is the second-best place to look
]

_HTML_HEADERS = {
    "User-Agent": CHROME_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

_FETCH_TIMEOUT = (4.0, 6.0)
_MAX_HTML_BYTES = 1_500_000  # 1.5 MB - enough for any contact page

_EMAIL_RE = re.compile(
    r"(?<![A-Za-z0-9._%+\-])"
    r"([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})"
    r"(?![A-Za-z0-9._%+\-])"
)
_MAILTO_RE = re.compile(r"""href=["']mailto:([^"'?#]+)""", re.IGNORECASE)
# "foo [at] bar [dot] com" / "foo (at) bar (dot) com" / "foo at bar dot com"
_OBFUSCATED_RE = re.compile(
    r"([A-Za-z0-9._%+\-]+)\s*[\[\(\{]?\s*at\s*[\]\)\}]?\s*"
    r"([A-Za-z0-9.\-]+)\s*[\[\(\{]?\s*dot\s*[\]\)\}]?\s*([A-Za-z]{2,})",
    re.IGNORECASE,
)

_BAD_LOCAL_PARTS = {
    "noreply", "no-reply", "donotreply", "do-not-reply", "mailer-daemon",
    "postmaster", "bounce", "bounces", "test", "user", "you", "your",
    "name", "email",
}
# Anything ending in one of these almost certainly isn't a contact email.
_BAD_DOMAINS = {
    "example.com", "example.org", "domain.com", "yoursite.com",
    "sentry.io", "wordpress.com", "wpengine.com", "cloudflare.com",
    "gstatic.com", "googleapis.com", "googletagmanager.com",
    "github.com", "schema.org", "w3.org",
}
_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".css", ".js")

# Local-part keyword scoring. Positive = looks like a useful inbox,
# negative = department we don't want to bother (sales, careers, etc.).
_KEYWORD_SCORES = {
    "editor": 7, "editors": 7, "newsroom": 7, "news": 6, "press": 6,
    "tips": 6, "story": 5, "stories": 5, "reporter": 5,
    "contact": 5, "hello": 4, "info": 3, "support": 2, "help": 2,
    "office": 1, "media": 4, "team": 2,
    "sales": -3, "careers": -3, "jobs": -3, "hr": -3, "recruiting": -4,
    "billing": -3, "payment": -3, "invoice": -3, "advertising": -2,
    "ads": -2, "subscribe": -3, "subscriptions": -3, "marketing": -1,
    "abuse": -1, "security": -1, "webmaster": -3,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _registrable(host: str) -> str:
    """Return a rough eTLD+1 (no public-suffix-list dep)."""
    parts = (host or "").strip().lower().lstrip(".").split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host or ""


def _is_junk_email(email: str) -> bool:
    if not email or "@" not in email or len(email) > 80:
        return True
    local, _, domain = email.partition("@")
    local = local.lower()
    domain = domain.lower()
    if not domain or "." not in domain:
        return True
    if domain in _BAD_DOMAINS:
        return True
    if local in _BAD_LOCAL_PARTS:
        return True
    if domain.endswith(_IMAGE_EXTS) or any(local.endswith(ext) for ext in _IMAGE_EXTS):
        return True
    if "/" in local or "\\" in local or local.startswith(".") or local.endswith("."):
        return True
    # Stripped Sentry / analytics noise like '0a1b2c@o12345.ingest.sentry.io'
    if "ingest.sentry" in domain:
        return True
    return False


def _score_email(email: str, *, source: str, page_path: str, host: str) -> int:
    local, _, domain = email.partition("@")
    local = local.lower()
    domain = domain.lower()
    score = 0

    if source == "mailto":
        score += 6  # Explicit mailto link is the strongest signal we can get.

    if "/contact" in page_path:
        score += 4
    elif "/about" in page_path or page_path in ("/staff", "/team", "/masthead"):
        score += 2
    # Homepage hits get nothing extra; footers are noisy.

    # Same registrable domain as the host we were asked about
    if _registrable(domain) == _registrable(host):
        score += 3
    # Exact same FQDN is even stronger
    if domain == host or domain == _registrable(host):
        score += 1

    for kw, delta in _KEYWORD_SCORES.items():
        if kw in local:
            score += delta

    return score


def _decode(body: bytes) -> str:
    try:
        return body.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _fetch_html(url: str) -> Optional[str]:
    try:
        with requests.get(
            url,
            headers=_HTML_HEADERS,
            timeout=_FETCH_TIMEOUT,
            stream=True,
            allow_redirects=True,
        ) as resp:
            if resp.status_code != 200:
                return None
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if "html" not in ctype and "xml" not in ctype:
                # Don't bother parsing PDFs, images, JSON.
                return None
            body = resp.raw.read(_MAX_HTML_BYTES + 1, decode_content=True)
            if not body:
                return None
            return _decode(body[:_MAX_HTML_BYTES])
    except Exception:
        return None


def _try_paths(host: str, path: str) -> Optional[Tuple[str, str]]:
    """Try https then http for a single path. Returns (path, html)."""
    for scheme in ("https", "http"):
        html = _fetch_html(f"{scheme}://{host}{path}")
        if html:
            return path, html
    return None


def _extract_emails(html: str) -> Iterable[Tuple[str, str]]:
    """Yield (email, source) tuples. `source` in {'mailto', 'text'}."""
    seen: set = set()
    for m in _MAILTO_RE.finditer(html):
        e = m.group(1).strip().lower()
        if e and e not in seen:
            seen.add(e)
            yield e, "mailto"
    for m in _EMAIL_RE.finditer(html):
        e = m.group(1).strip().lower()
        if e and e not in seen:
            seen.add(e)
            yield e, "text"
    for m in _OBFUSCATED_RE.finditer(html):
        e = f"{m.group(1)}@{m.group(2)}.{m.group(3)}".lower()
        if e and e not in seen:
            seen.add(e)
            yield e, "text"


def _hunter_lookup(host: str) -> List[Tuple[int, str]]:
    """Optional Hunter.io fallback. No-op unless HUNTER_API_KEY is set."""
    api_key = os.environ.get("HUNTER_API_KEY")
    if not api_key or not host:
        return []
    try:
        resp = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": _registrable(host), "api_key": api_key, "limit": 10},
            timeout=6,
        )
        if resp.status_code != 200:
            return []
        data = resp.json().get("data") or {}
        out: List[Tuple[int, str]] = []
        for entry in data.get("emails", []):
            email = (entry.get("value") or "").lower()
            if not email or _is_junk_email(email):
                continue
            confidence = int(entry.get("confidence") or 0)
            # Map Hunter's 0-100 confidence into our scoring scale and add a
            # small bonus so it competes with weak heuristic hits but doesn't
            # automatically beat a strong mailto on the contact page.
            score = max(1, confidence // 12)
            for kw, delta in _KEYWORD_SCORES.items():
                if kw in email.split("@", 1)[0]:
                    score += delta
            out.append((score, email))
        return out
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=512)
def find_contact(host: str) -> Optional[dict]:
    """
    Return `{'email': str, 'source': 'mailto'|'text'|'hunter'|'guess',
    'page_url': Optional[str]}` for the best contact we can find, or None.

    Cached per-host - subsequent lookups during the same session return
    instantly even though the first call may take a few seconds.
    """
    if not host:
        return None

    started = time.time()
    candidates: List[Tuple[int, str, str, str]] = []  # (score, email, source, page_url)

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_try_paths, host, p): p for p in _CONTACT_PATHS}
        try:
            for fut in as_completed(futures, timeout=12):
                got = fut.result()
                if not got:
                    continue
                path, html = got
                page_url = f"https://{host}{path}"
                for email, source in _extract_emails(html):
                    if _is_junk_email(email):
                        continue
                    score = _score_email(email, source=source, page_path=path, host=host)
                    candidates.append((score, email, source, page_url))
                # Early exit: if we already have a strong contact-page mailto,
                # no need to keep waiting on the slower paths.
                if candidates and time.time() - started > 3:
                    best = max(c[0] for c in candidates)
                    if best >= 10:
                        break
        except Exception:
            pass

    # Optional Hunter.io top-up
    for score, email in _hunter_lookup(host):
        candidates.append((score, email, "hunter", None))

    if not candidates:
        return None

    # Best score wins; alphabetical tiebreak for determinism.
    candidates.sort(key=lambda c: (-c[0], c[1]))
    score, email, source, page_url = candidates[0]
    if score <= 0:
        return None
    return {"email": email, "source": source, "page_url": page_url, "score": score}


def find_contact_email(host: str) -> Optional[str]:
    """Convenience wrapper - returns just the email, or None."""
    info = find_contact(host)
    return info["email"] if info else None
