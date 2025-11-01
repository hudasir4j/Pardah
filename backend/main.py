from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from search_images import search_images_bing
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

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
        
        # Search for images using the user's search terms
        # Try multiple search queries to get more results
        search_queries = [
            search_terms,
            f"{search_terms} instagram",
            f"{search_terms} facebook",
            f"{search_terms} person",
        ]
        
        all_search_results = []
        for query in search_queries:
            print(f"\n[Upload] Searching for: '{query}'")
            results = search_images_bing(query=query, max_images=10)
            all_search_results.extend(results)
            print(f"[Upload] Found {len(results)} images for '{query}'")
        
        if not all_search_results:
            return jsonify({'error': 'No images found for those search terms. Try different terms.', 'matches': []}), 200
        
        print(f"\n[Upload] Total images found: {len(all_search_results)}")
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for result in all_search_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        print(f"[Upload] Unique images after dedup: {len(unique_results)}")
        
        # Match faces - find images of THIS SPECIFIC PERSON
        print(f"\n[Upload] Starting face matching...")
        matched_images = match_faces(
            user_embedding=user_embedding,
            search_results=unique_results,
            threshold=0.5  # Slightly higher threshold for more confidence
        )
        
        print(f"[Upload] Found {len(matched_images)} matching images")
        
        return jsonify({
            'status': 'success',
            'matches': matched_images,
            'count': len(matched_images),
            'uploaded_file': filename,
            'search_terms': search_terms
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
    app.run(debug=True, port=5000)