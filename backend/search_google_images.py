"""
Google Images search via SerpApi.
Returns image URLs and page URLs for face matching and takedown flows.
Set SERPAPI_API_KEY in .env to enable (optional; search still works with Bing + DuckDuckGo if unset).
"""
import os
import requests

SERPAPI_BASE = "https://serpapi.com/search"


def search_images_google(query: str, max_images: int = 10, api_key: str = None) -> list:
    """
    Search Google Images using SerpApi.

    Args:
        query: Search terms (e.g. "name", "username instagram")
        max_images: Max number of results to return
        api_key: SerpApi API key (defaults to SERPAPI_API_KEY env var)

    Returns:
        List of dicts: { "url": image_url, "page_url": link, "title": str, "source": "Google Images" }
    """
    key = api_key or os.environ.get("SERPAPI_API_KEY")
    if not key:
        print("[Search] Google Images skipped: SERPAPI_API_KEY not set")
        return []

    try:
        print(f"[Search] Searching Google Images for: '{query}'")
        params = {
            "engine": "google_images",
            "q": query,
            "api_key": key,
            "num": min(max_images, 100),
        }
        resp = requests.get(SERPAPI_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # SerpApi returns images in "images_results" with "image" (URL) and "link" (page)
        raw = data.get("images_results") or []
        results = []
        for i, item in enumerate(raw[:max_images]):
            image_url = item.get("image") or item.get("original")
            link = item.get("link") or image_url
            title = item.get("title") or ""
            if not image_url:
                continue
            results.append({
                "url": image_url,
                "page_url": link,
                "title": title or f"Google Images result {i + 1}",
                "source": "Google Images",
            })
        print(f"[Search] Google Images returned {len(results)} results")
        return results
    except requests.RequestException as e:
        print(f"[Search] Google Images request error: {e}")
        return []
    except Exception as e:
        print(f"[Search] Google Images error: {e}")
        import traceback
        traceback.print_exc()
        return []
