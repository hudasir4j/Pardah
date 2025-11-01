from bing_image_downloader import bing_image_downloader
import os
import requests
from PIL import Image
from io import BytesIO

def search_images_bing(query="person", max_images=15):
    """
    Search for images using Bing Image Search
    Returns: list of image URLs with metadata
    
    NOTE: For a real product, you'd want to use the Bing Search API
    This is a quick workaround for hackathon
    """
    try:
        # Create temp directory for downloads
        download_dir = "temp_search_results"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        # Download images
        bing_image_downloader.download(
            query,
            limit=max_images,
            output_dir="dataset",
            adult_filter_off=True,
            force_replace=False,
            timeout=60,
            verbose=False
        )
        
        # Extract URLs (this is a bit hacky, but works for MVP)
        results = []
        search_dir = f"dataset/{query}"
        
        if os.path.exists(search_dir):
            for img_file in os.listdir(search_dir)[:max_images]:
                img_path = os.path.join(search_dir, img_file)
                results.append({
                    'url': img_path,  # For MVP, using local path
                    'title': img_file,
                    'source': 'bing',
                })
        
        return results
    
    except Exception as e:
        print(f"Error searching images: {e}")
        return []

def search_images_bing_api(query="person", max_images=15, api_key=None):
    """
    Alternative: Use actual Bing Search API (requires API key)
    This is more reliable but needs authentication
    """
    if not api_key:
        print("No Bing API key provided")
        return []
    
    try:
        search_url = "https://api.bing.microsoft.com/v7.0/images/search"
        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {
            "q": query,
            "count": max_images,
            "imageType": "Photo"
        }
        
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        search_results = response.json()
        results = []
        
        for image in search_results.get('value', []):
            results.append({
                'url': image.get('contentUrl'),
                'title': image.get('name'),
                'source': image.get('hostPageUrl'),
                'thumbnail': image.get('thumbnailUrl')
            })
        
        return results
    
    except Exception as e:
        print(f"Error with Bing API: {e}")
        return []

def validate_image_url(image_url):
    """
    Check if URL is valid and contains an actual image
    """
    try:
        response = requests.head(image_url, timeout=5)
        content_type = response.headers.get('content-type', '')
        
        return 'image' in content_type.lower()
    
    except Exception as e:
        print(f"Error validating image URL: {e}")
        return False