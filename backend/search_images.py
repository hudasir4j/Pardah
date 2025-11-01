from bing_image_downloader.bing import Bing
import os

def search_images_bing(query="person", max_images=10):
    """
    Search for images using Bing Image Search based on user's search terms
    This finds images of the SPECIFIC PERSON the user searches for
    
    Args:
        query: Search terms (e.g., "Huda Siraj", "username instagram")
        max_images: Number of images to download
    
    Returns: list of image paths with metadata
    """
    try:
        print(f"[Search] Searching Bing for: '{query}'")
        
        # Create dataset folder
        dataset_dir = "dataset"
        if not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir)
        
        # Sanitize query for folder name
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-')).rstrip()
        
        # Create Bing downloader instance
        bing = Bing(
            query,
            limit=max_images,
            output_dir=dataset_dir,
            adult_filter_off=True,
            force_replace=False,
            timeout=60,
            verbose=False
        )
        
        print(f"[Search] Starting download...")
        bing.download()
        print(f"[Search] Download complete")
        
        # Get results from downloaded folder
        results = []
        search_dir = os.path.join(dataset_dir, safe_query)
        
        if os.path.exists(search_dir):
            files = os.listdir(search_dir)
            print(f"[Search] Found {len(files)} images for '{query}'")
            
            for img_file in files[:max_images]:
                img_path = os.path.join(search_dir, img_file)
                
                if os.path.isfile(img_path) and img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    results.append({
                        'url': img_path,
                        'title': img_file,
                        'source': f'bing-search:{query}',
                    })
        else:
            print(f"[Search] Search directory not found: {search_dir}")
        
        print(f"[Search] Returning {len(results)} image paths")
        return results
    
    except Exception as e:
        print(f"[Search] Error during search: {e}")
        import traceback
        traceback.print_exc()
        return []

def validate_image_url(image_url):
    """Check if image exists"""
    try:
        return os.path.exists(image_url)
    except Exception as e:
        print(f"Error validating image: {e}")
        return False