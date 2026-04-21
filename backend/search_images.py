"""
Bing image search.

We only need URLs here; actual downloading + face embedding happens in the
unified, parallelized pipeline in face_recognition.py. The previous
implementation used bing-image-downloader, which (1) tried to download every
URL inline, (2) failed noisily on Instagram crawler URLs and CDN 403s, and
(3) paginated up to 16 pages looking for valid images. We replace it with a
single HTML scrape of Bing's async images endpoint.
"""
from __future__ import annotations

import re
import urllib.parse
from typing import List, Dict

from http_client import get_session, DEFAULT_TIMEOUT


BING_ASYNC_URL = "https://www.bing.com/images/async"
BING_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Bing embeds the JSON blob for each tile as HTML-entity-encoded attributes;
# "murl" is the original media URL and "purl" is the page that hosts it.
_MURL_RE = re.compile(r"murl&quot;:&quot;(.*?)&quot;")
_PURL_RE = re.compile(r"purl&quot;:&quot;(.*?)&quot;")
_TITLE_RE = re.compile(r"t&quot;:&quot;(.*?)&quot;")


def _decode(s: str) -> str:
    return (
        s.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("\\u0026", "&")
        .replace("\\/", "/")
    )


def _parse_tiles(html: str) -> List[Dict[str, str]]:
    """
    Parse Bing's async-images HTML for image tiles. Each tile is represented
    by a JSON blob embedded as HTML-encoded attributes. We grab `murl`,
    `purl`, and `t` (title) position-aligned.
    """
    murls = _MURL_RE.findall(html)
    purls = _PURL_RE.findall(html)
    titles = _TITLE_RE.findall(html)

    tiles: List[Dict[str, str]] = []
    for i, murl in enumerate(murls):
        tiles.append(
            {
                "url": _decode(murl),
                "page_url": _decode(purls[i]) if i < len(purls) else _decode(murl),
                "title": _decode(titles[i]) if i < len(titles) else f"Bing result {i + 1}",
            }
        )
    return tiles


def search_images_bing(query: str = "person", max_images: int = 10) -> List[Dict[str, str]]:
    """
    Return a list of `{url, page_url, title, source}` dicts for a Bing image
    search. No disk I/O, no downloads.
    """
    try:
        print(f"[Search] Searching Bing for: '{query}'")
        session = get_session()

        results: List[Dict[str, str]] = []
        seen_urls = set()
        # Stop after 3 pages if we still don't have enough - prevents the
        # 16-page hunt seen in the old terminal logs.
        max_pages = 3
        for page in range(max_pages):
            params = {
                "q": query,
                "first": page * 30,
                "count": max(max_images * 2, 30),
                "adlt": "off",
            }
            try:
                resp = session.get(
                    BING_ASYNC_URL,
                    params=params,
                    headers=BING_HEADERS,
                    timeout=DEFAULT_TIMEOUT,
                )
            except Exception as e:
                print(f"[Search] Bing request failed: {e}")
                break
            if resp.status_code != 200:
                print(f"[Search] Bing returned HTTP {resp.status_code}")
                break

            tiles = _parse_tiles(resp.text)
            if not tiles:
                # No more results.
                break

            for t in tiles:
                if t["url"] in seen_urls:
                    continue
                seen_urls.add(t["url"])
                results.append(
                    {
                        "url": t["url"],
                        "page_url": t.get("page_url") or t["url"],
                        "title": t.get("title") or "Bing result",
                        "source": "Bing Images",
                    }
                )
                if len(results) >= max_images:
                    break

            if len(results) >= max_images:
                break

        print(f"[Search] Bing returned {len(results)} URLs")
        return results[:max_images]
    except Exception as e:
        print(f"[Search] Bing error: {e}")
        import traceback

        traceback.print_exc()
        return []


def validate_image_url(image_url: str) -> bool:
    """Kept for backwards compatibility; not used in the new pipeline."""
    import os

    try:
        return os.path.exists(image_url)
    except Exception:
        return False
