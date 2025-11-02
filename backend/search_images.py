from bing_image_downloader.bing import Bing
from pathlib import Path
import os
import shutil

def search_images_bing(query="person", max_images=10):
    """
    Search for images using Bing Image Search based on user's search terms
    This finds images of the SPECIFIC PERSON the user searches for
    
    Args:
        query: Search terms (e.g., "Beyonce", "username instagram")
        max_images: Number of images to download
    
    Returns: list of image paths with metadata
    """
    try:
        print(f"[Search] Searching Bing for: '{query}'")
        
        # Create dataset folder if it doesn't exist
        dataset_dir = Path("dataset")
        dataset_dir.mkdir(exist_ok=True)
        
        # Sanitize query for folder name
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-')).rstrip()
        search_dir = dataset_dir / safe_query
        
        # Clean up old results for this search
        if search_dir.exists():
            shutil.rmtree(search_dir)
        search_dir.mkdir(exist_ok=True)
        
        # Download images using Bing class
        try:
            print(f"[Search] Starting Bing download to {search_dir}...")
            bing = Bing(
                query,
                limit=max_images,
                output_dir=dataset_dir,
                adult='off',
                timeout=60
            )
            bing.run()
            print(f"[Search] Bing download complete")
        except Exception as e:
            print(f"[Search] Download error: {e}")
            return []
        
        # Find downloaded images in dataset root and move them to query folder
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif')
        all_images = []
        
        # Look for images in dataset_dir (root)
        for ext in image_extensions:
            all_images.extend(dataset_dir.glob(f'*{ext}'))
            all_images.extend(dataset_dir.glob(f'*{ext.upper()}'))
        
        print(f"[Search] Found {len(all_images)} downloaded images in dataset root")
        
        # Move them to the query-specific folder
        results = []
        for img_path in all_images[:max_images]:
            try:
                dest = search_dir / img_path.name
                shutil.move(str(img_path), str(dest))
                results.append({
                    'url': str(dest),
                    'title': img_path.name,
                    'source': f'bing-search:{query}',
                })
            except Exception as e:
                print(f"[Search] Error moving image {img_path.name}: {e}")
        
        print(f"[Search] Returning {len(results)} image paths from {search_dir}")
        return results
    
    except Exception as e:
        print(f"[Search] Error during search: {e}")
        import traceback
        traceback.print_exc()
        return []

def validate_image_url(image_url):
    """
    Check if image file exists
    """
    try:
        return os.path.exists(image_url)
    except Exception as e:
        print(f"Error validating image: {e}")
        return False