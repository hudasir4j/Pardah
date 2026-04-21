"""
DuckDuckGo Images search (no API key required).
Returns image URLs for face matching; source label "DuckDuckGo Images".

Note: the upstream library was renamed from `duckduckgo_search` to `ddgs`.
We try the new name first and fall back to the old one for compatibility.
"""
from __future__ import annotations

from typing import List, Dict

try:  # preferred, current package name
    from ddgs import DDGS  # type: ignore
except ImportError:  # pragma: no cover - legacy fallback
    from duckduckgo_search import DDGS  # type: ignore


def search_images_duckduckgo(query: str, max_images: int = 10) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo Images.

    Returns:
        List of dicts: { "url": image_url, "page_url": link, "title": str, "source": "DuckDuckGo Images" }
    """
    try:
        print(f"[Search] Searching DuckDuckGo Images for: '{query}'")
        # Older `duckduckgo_search.DDGS` uses .images(...); newer `ddgs.DDGS`
        # keeps the same method signature.
        with DDGS() as ddgs:
            results_raw = list(ddgs.images(query=query, max_results=max_images)) \
                if _accepts_kwarg(ddgs.images, "query") \
                else list(ddgs.images(keywords=query, max_results=max_images))
        results: List[Dict[str, str]] = []
        for i, item in enumerate(results_raw):
            image_url = item.get("image")
            page_url = item.get("url") or image_url
            title = item.get("title") or ""
            if not image_url:
                continue
            results.append(
                {
                    "url": image_url,
                    "page_url": page_url,
                    "title": title or f"DuckDuckGo result {i + 1}",
                    "source": "DuckDuckGo Images",
                }
            )
        print(f"[Search] DuckDuckGo Images returned {len(results)} results")
        return results
    except Exception as e:
        print(f"[Search] DuckDuckGo Images error: {e}")
        import traceback

        traceback.print_exc()
        return []


def _accepts_kwarg(fn, name: str) -> bool:
    """ddgs renamed `keywords` -> `query`; detect which the installed lib uses."""
    try:
        import inspect

        return name in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False
