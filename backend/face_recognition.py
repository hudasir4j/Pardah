from deepface import DeepFace
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import hashlib

def extract_face_embedding(image_path):
    """
    Load an image and extract face embedding using DeepFace
    Returns: numpy array of face embedding, or None if no face found
    
    Args:
        image_path: Path to image file (local or URL)
    
    Returns:
        numpy array of 512 numbers representing the face, or None
    """
    try:
        print(f"[Face] Extracting embedding from: {image_path}")
        
        # DeepFace returns embeddings as a list of dicts
        result = DeepFace.represent(img_path=image_path, model_name="Facenet512", enforce_detection=True)
        
        if len(result) == 0:
            print(f"[Face] No face found in image")
            return None
        
        # Return first face embedding (as numpy array)
        embedding = np.array(result[0]['embedding'])
        print(f"[Face] Embedding extracted successfully (512-dim vector)")
        return embedding
    
    except Exception as e:
        print(f"[Face] Error extracting embedding: {e}")
        return None

def extract_face_embedding_from_url(image_url):
    """
    Download image from URL and extract face embedding
    
    Args:
        image_url: URL or local path to image
    
    Returns:
        numpy array of face embedding, or None
    """
    try:
        # Handle both URLs and local file paths
        if image_url.startswith('http'):
            response = requests.get(image_url, timeout=5)
            image = Image.open(BytesIO(response.content))
        else:
            # Local file path
            image = Image.open(image_url)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save temporarily for deepface
        temp_path = '/tmp/temp_face.jpg'
        image.save(temp_path)
        
        # Extract embedding
        result = DeepFace.represent(img_path=temp_path, model_name="Facenet512", enforce_detection=True)
        
        if len(result) == 0:
            return None
        
        embedding = np.array(result[0]['embedding'])
        return embedding
    
    except Exception as e:
        print(f"[Face] Error extracting face from URL {image_url}: {e}")
        return None

def compare_faces(user_embedding, search_embedding, threshold=0.5):
    """
    Compare two face embeddings using Euclidean distance
    
    Args:
        user_embedding: numpy array of user's face (512 dims)
        search_embedding: numpy array of image to compare (512 dims)
        threshold: distance threshold for matching (lower = stricter)
    
    Returns:
        tuple: (is_match: bool, distance: float)
        
    Distance interpretation:
    - < 0.4: Very likely same person
    - 0.4-0.5: Probably same person
    - 0.5-0.7: Uncertain
    - > 0.7: Different people
    """
    try:
        # Calculate Euclidean distance
        distance = np.linalg.norm(user_embedding - search_embedding)
        is_match = distance < threshold
        return is_match, distance
    except Exception as e:
        print(f"[Face] Error comparing faces: {e}")
        return False, 1.0

def match_faces(user_embedding, search_results, threshold=0.5):
    """
    Compare user's face against all search results
    Finds images of THIS SPECIFIC PERSON by comparing face embeddings
    
    Args:
        user_embedding: numpy array of user's face embedding
        search_results: list of image results with 'url' key
        threshold: distance threshold for matching
    
    Returns:
        list of matching images sorted by similarity (best first)
    """
    matches = []
    
    print(f"\n[Face Matching] Starting to match {len(search_results)} images...")
    print(f"[Face Matching] Threshold: {threshold} (lower = stricter matching)")
    
    for idx, result in enumerate(search_results):
        try:
            image_url = result.get('url')
            image_title = result.get('title', 'Unknown')
            
            print(f"[Face Matching] Processing {idx + 1}/{len(search_results)}: {image_title}")
            
            # Extract face from search result image
            search_embedding = extract_face_embedding_from_url(image_url)
            
            if search_embedding is None:
                print(f"  ✗ No face detected")
                continue
            
            # Compare faces
            is_match, distance = compare_faces(user_embedding, search_embedding, threshold)
            
            # Normalize similarity to 0-1 range
            similarity = float(1 - (distance / 2))
            
            if is_match:
                # Get image hash for reporting
                img_hash = get_image_hash(image_url)
                
                match_data = {
                    'url': image_url,
                    'title': image_title,
                    'source': result.get('source', 'Unknown'),
                    'similarity_score': similarity,
                    'distance': float(distance),
                    'image_hash': img_hash
                }
                
                matches.append(match_data)
                print(f"  ✓ MATCH FOUND! Distance: {distance:.3f}, Similarity: {similarity:.1%}")
            else:
                print(f"  ✗ Not a match (distance: {distance:.3f}, needed: < {threshold})")
        
        except Exception as e:
            print(f"  ✗ Error processing image: {e}")
            continue
    
    # Sort by similarity (most similar first)
    matches.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    print(f"\n[Face Matching] Complete! Found {len(matches)} matching images\n")
    return matches

def get_image_hash(image_url):
    """
    Download image and compute SHA256 hash
    Useful for reporting to Google
    
    Args:
        image_url: URL or local path to image
    
    Returns:
        SHA256 hash of image as hex string
    """
    try:
        if image_url.startswith('http'):
            response = requests.get(image_url, timeout=5)
            image_data = response.content
        else:
            # Local file
            with open(image_url, 'rb') as f:
                image_data = f.read()
        
        image_hash = hashlib.sha256(image_data).hexdigest()
        return image_hash
    except Exception as e:
        print(f"[Face] Error hashing image: {e}")
        return None