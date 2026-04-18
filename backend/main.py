"""
Startup: ensure TensorFlow 2.15 + Keras is available before importing deepface.
The standalone 'keras' package (pulled in by deepface) can conflict; we load tensorflow.keras first.
"""
import sys
import os
try:
    import tensorflow as tf
    # Force tensorflow.keras submodule to load so deepface's "from tensorflow.keras..." works
    import tensorflow.keras  # noqa: F401
except ImportError:
    print("TensorFlow/Keras not available.", file=sys.stderr)
    print("From the backend folder, run:", file=sys.stderr)
    print("  pip3 install --user \"tensorflow>=2.15.0,<2.16\"", file=sys.stderr)
    print("Or use a venv: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from urllib.parse import urlsplit, urlunsplit
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from search_images import search_images_bing
from search_google_images import search_images_google
from search_duckduckgo_images import search_images_duckduckgo
from face_recognition import extract_face_embedding, match_faces
from report_generator import generate_report_link

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def get_env_int(name, default):
    try:
        return int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default


def normalize_url_for_dedup(raw_url):
    if not raw_url:
        return raw_url
    if raw_url.startswith("http://") or raw_url.startswith("https://"):
        parts = urlsplit(raw_url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    return raw_url


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/image/<path:filepath>', methods=['GET'])
def serve_image(filepath):
    """
    Serve images from the dataset folder
    """
    try:
        import urllib.parse
        decoded_path = urllib.parse.unquote(filepath)
        print(f"[Image] Serving: {decoded_path}")
        return send_file(decoded_path)
    except Exception as e:
        print(f"[Image] Error: {e}")
        return jsonify({'error': str(e)}), 404

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    User uploads their photo with hijab AND provides search terms
    Extract face embedding and search for images matching those terms
    """
    try:
        # Check for file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Check for search terms
        search_terms = request.form.get('search_terms', '').strip()
        if not search_terms:
            return jsonify({'error': 'Please provide search terms (name, username, etc.)'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"\n[Upload] File saved: {filepath}")
        print(f"[Upload] Search terms: {search_terms}")
        
        # Extract face embedding from uploaded image
        print(f"[Upload] Extracting face embedding from user's photo...")
        user_embedding = extract_face_embedding(filepath)
        if user_embedding is None:
            return jsonify({'error': 'No face detected in image'}), 400
        
        print(f"[Upload] Face embedding extracted successfully")
        
        # Search configuration (set small values in .env for fast MVP testing)
        images_per_source = get_env_int("IMAGES_PER_SOURCE", 3)
        max_search_queries = get_env_int("MAX_SEARCH_QUERIES", 2)
        max_candidate_images = get_env_int("MAX_CANDIDATE_IMAGES", 15)
        max_matched_images = get_env_int("MAX_MATCHED_IMAGES", 8)

        # Search for images using the user's search terms (multiple sources)
        search_queries = [
            search_terms,
            f"{search_terms} instagram",
            f"{search_terms} facebook",
            f"{search_terms} person",
        ]
        search_queries = search_queries[:max_search_queries]

        all_search_results = []
        source_counts = {"Bing Images": 0, "Google Images": 0, "DuckDuckGo Images": 0}
        source_notes = []
        if not os.environ.get("SERPAPI_API_KEY"):
            source_notes.append("Google Images is disabled until SERPAPI_API_KEY is set in backend/.env")

        for query in search_queries:
            print(f"\n[Upload] Searching for: '{query}'")
            # Bing Images (local download)
            bing_results = search_images_bing(query=query, max_images=images_per_source)
            all_search_results.extend(bing_results)
            source_counts["Bing Images"] += len(bing_results)
            print(f"[Upload] Bing: {len(bing_results)} images")
            # Google Images (SerpApi; optional if SERPAPI_API_KEY set)
            google_results = search_images_google(query=query, max_images=images_per_source)
            all_search_results.extend(google_results)
            source_counts["Google Images"] += len(google_results)
            print(f"[Upload] Google Images: {len(google_results)} images")
            # DuckDuckGo Images (no API key)
            ddg_results = search_images_duckduckgo(query=query, max_images=images_per_source)
            all_search_results.extend(ddg_results)
            source_counts["DuckDuckGo Images"] += len(ddg_results)
            print(f"[Upload] DuckDuckGo Images: {len(ddg_results)} images")
        
        if not all_search_results:
            return jsonify({'error': 'No images found for those search terms. Try different terms.', 'matches': []}), 200
        
        print(f"\n[Upload] Total images found: {len(all_search_results)}")
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for result in all_search_results:
            dedup_key = normalize_url_for_dedup(result.get('url'))
            if dedup_key not in seen_urls:
                seen_urls.add(dedup_key)
                unique_results.append(result)
        
        print(f"[Upload] Unique images after dedup: {len(unique_results)}")
        unique_results = unique_results[:max_candidate_images]
        print(f"[Upload] Candidate images after limit: {len(unique_results)}")
        
        # Match faces - find images of THIS SPECIFIC PERSON
        print(f"\n[Upload] Starting face matching...")
        matched_images = match_faces(
            user_embedding=user_embedding,
            search_results=unique_results,
            threshold=0.5
        )
        
        print(f"[Upload] Found {len(matched_images)} matching images")
        # Deduplicate final matches using image hash first, then URL fallback
        deduped_matches = []
        seen_match_keys = set()
        for match in matched_images:
            match_key = match.get("image_hash") or normalize_url_for_dedup(match.get("url"))
            if match_key in seen_match_keys:
                continue
            seen_match_keys.add(match_key)
            deduped_matches.append(match)
        matched_images = deduped_matches[:max_matched_images]
        print(f"[Upload] Final deduped matches: {len(matched_images)}")
        
        # Convert local paths to accessible URLs
        for match in matched_images:
            if match['url'].startswith('dataset/'):
                # Convert to URL that frontend can access
                match['url'] = f"http://localhost:5000/image/{match['url']}"
        
        return jsonify({
            'status': 'success',
            'matches': matched_images,
            'count': len(matched_images),
            'uploaded_file': filename,
            'search_terms': search_terms,
            'search_debug': {
                'queries_used': search_queries,
                'limits': {
                    'images_per_source': images_per_source,
                    'max_search_queries': max_search_queries,
                    'max_candidate_images': max_candidate_images,
                    'max_matched_images': max_matched_images,
                },
                'source_counts': source_counts,
                'source_notes': source_notes,
            }
        }), 200
    
    except Exception as e:
        print(f"[Upload] Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/report', methods=['POST'])
def generate_report():
    """
    Generate pre-filled Google report link for image removal
    """
    try:
        data = request.json
        image_url = data.get('image_url')
        image_hash = data.get('image_hash')
        
        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400
        
        report_link = generate_report_link(image_url, image_hash)
        
        return jsonify({
            'status': 'success',
            'report_link': report_link
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify-match', methods=['POST'])
def verify_match():
    """
    User confirms if matched image is actually them
    Stores verification for analytics
    """
    try:
        data = request.json
        image_url = data.get('image_url')
        is_match = data.get('is_match')  # True/False
        
        print(f"\n[Verify] Image: {image_url}")
        print(f"[Verify] User confirmation: {'This is me' if is_match else 'Not me'}")
        
        return jsonify({
            'status': 'success',
            'verified': is_match
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("Starting Reclaim Backend Server")
    print("="*60)
    print("Server running on: http://localhost:5000")
    print("Health check: http://localhost:5000/health")
    print("="*60 + "\n")
    app.run(debug=False, port=5000)