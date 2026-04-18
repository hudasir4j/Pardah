"""
DuckDuckGo Images search (no API key required).
Returns image URLs for face matching; source label "DuckDuckGo Images".
"""
from duckduckgo_search import DDGS


def search_images_duckduckgo(query: str, max_images: int = 10) -> list:
    """
    Search DuckDuckGo Images.

    Args:
        query: Search terms (e.g. "name", "username instagram")
        max_images: Max number of results to return

    Returns:
        List of dicts: { "url": image_url, "page_url": link, "title": str, "source": "DuckDuckGo Images" }
    """
    try:
        print(f"[Search] Searching DuckDuckGo Images for: '{query}'")
        # DDGS().images returns list of dicts with "image", "url", "title"
        results_raw = list(
            DDGS().images(keywords=query, max_results=max_images)
        )
        results = []
        for i, item in enumerate(results_raw):
            # "image" is the direct image URL; "url" is the page link
            image_url = item.get("image")
            page_url = item.get("url") or image_url
            title = item.get("title") or ""
            if not image_url:
                continue
            results.append({
                "url": image_url,
                "page_url": page_url,
                "title": title or f"DuckDuckGo result {i + 1}",
                "source": "DuckDuckGo Images",
            })
        print(f"[Search] DuckDuckGo Images returned {len(results)} results")
        return results
    except Exception as e:
        print(f"[Search] DuckDuckGo Images error: {e}")
        import traceback
        traceback.print_exc()
        return []
