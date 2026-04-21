"""
Startup: ensure TensorFlow 2.15 + Keras is available before importing deepface.
The standalone 'keras' package (pulled in by deepface) can conflict; we load tensorflow.keras first.
"""
import sys
import os
try:
    import tensorflow as tf  # noqa: F401
    # Force tensorflow.keras submodule to load so deepface's "from tensorflow.keras..." works
    import tensorflow.keras  # noqa: F401
except ImportError:
    print("TensorFlow/Keras not available.", file=sys.stderr)
    print("From the backend folder, run:", file=sys.stderr)
    print("  pip3 install --user \"tensorflow>=2.15.0,<2.16\"", file=sys.stderr)
    print("Or use a venv: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlsplit, urlunsplit

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from search_images import search_images_bing
from search_google_images import search_images_google
from search_duckduckgo_images import search_images_duckduckgo
from face_recognition import extract_face_embedding, match_faces
from report_generator import generate_report_link, build_removal_plan

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

# Hosts/URL patterns we never want to try to download. These are pure-HTML
# crawler landing pages, tracking pixels, or dead ad networks that just waste
# bandwidth and emit scary error messages. Instagram/Facebook crawler URLs
# are NOT on this list: the social resolver upgrades them to real CDN URLs.
_BLOCKED_URL_PATTERNS = [
    re.compile(r"^https?://(www\.)?google\.com/imgres\b"),
    re.compile(r"\bdoubleclick\.net\b"),
    re.compile(r"\badservice\.google\."),
    re.compile(r"\.gif(\?|$)"),  # animated GIFs rarely have usable face frames
]


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


def is_blocked_url(url: str) -> bool:
    if not url:
        return True
    for pat in _BLOCKED_URL_PATTERNS:
        if pat.search(url):
            return True
    return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/image/<path:filepath>', methods=['GET'])
def serve_image(filepath):
    """Serve images from the dataset folder (legacy — kept for any existing links)."""
    try:
        import urllib.parse
        decoded_path = urllib.parse.unquote(filepath)
        print(f"[Image] Serving: {decoded_path}")
        return send_file(decoded_path)
    except Exception as e:
        print(f"[Image] Error: {e}")
        return jsonify({'error': str(e)}), 404


# Each source callable matches signature: (query: str, max_images: int) -> list
_SEARCH_SOURCES = {
    "Bing Images": search_images_bing,
    "Google Images": search_images_google,
    "DuckDuckGo Images": search_images_duckduckgo,
}


def _run_source(source_name: str, fn, query: str, max_images: int):
    """Shim used by the ThreadPool so we know which source each future belongs to."""
    try:
        return source_name, query, fn(query=query, max_images=max_images)
    except Exception as e:
        print(f"[Search] {source_name} failed for '{query}': {e}")
        return source_name, query, []


@app.route('/upload', methods=['POST'])
def upload_image():
    """
    User uploads their photo with hijab AND provides search terms.
    Extract face embedding and search for images matching those terms across
    Bing, Google (via SerpApi), and DuckDuckGo - all fanned out in parallel.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        search_terms = request.form.get('search_terms', '').strip()
        if not search_terms:
            return jsonify({'error': 'Please provide search terms (name, username, etc.)'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        print(f"\n[Upload] File saved: {filepath}")
        print(f"[Upload] Search terms: {search_terms}")

        print("[Upload] Extracting face embedding from user's photo...")
        user_embedding = extract_face_embedding(filepath)
        if user_embedding is None:
            return jsonify({'error': 'No face detected in image'}), 400
        print("[Upload] Face embedding extracted successfully")

        images_per_source = get_env_int("IMAGES_PER_SOURCE", 3)
        max_search_queries = get_env_int("MAX_SEARCH_QUERIES", 2)
        max_candidate_images = get_env_int("MAX_CANDIDATE_IMAGES", 15)
        max_matched_images = get_env_int("MAX_MATCHED_IMAGES", 8)

        # Broader query set: users want results from every major social platform,
        # not just "name" alone. Instagram/Facebook/TikTok queries surface
        # social profiles Bing wouldn't rank highly for a bare-name query.
        search_queries = [
            search_terms,
            f"{search_terms} instagram",
            f"{search_terms} facebook",
            f"{search_terms} tiktok",
            f"{search_terms} linkedin",
            f"{search_terms} twitter",
        ]
        search_queries = search_queries[:max_search_queries]

        source_counts = {name: 0 for name in _SEARCH_SOURCES}
        source_notes = []
        if not os.environ.get("SERPAPI_API_KEY"):
            source_notes.append(
                "Google Images is disabled until SERPAPI_API_KEY is set in backend/.env"
            )

        # Fan out: every (source, query) pair runs in parallel.
        fan_out_jobs = [
            (source_name, fn, query)
            for source_name, fn in _SEARCH_SOURCES.items()
            for query in search_queries
        ]

        all_search_results = []
        print(
            f"\n[Upload] Running {len(fan_out_jobs)} search jobs in parallel "
            f"({len(_SEARCH_SOURCES)} sources x {len(search_queries)} queries)"
        )
        with ThreadPoolExecutor(max_workers=min(12, max(2, len(fan_out_jobs)))) as pool:
            futures = [
                pool.submit(_run_source, name, fn, q, images_per_source)
                for name, fn, q in fan_out_jobs
            ]
            for fut in as_completed(futures):
                source_name, query, results = fut.result()
                source_counts[source_name] = source_counts.get(source_name, 0) + len(results)
                all_search_results.extend(results)
                print(f"[Upload] {source_name} ({query}): {len(results)} images")

        if not all_search_results:
            return jsonify({
                'error': 'No images found for those search terms. Try different terms.',
                'matches': [],
                'search_debug': {
                    'queries_used': search_queries,
                    'source_counts': source_counts,
                    'source_notes': source_notes,
                },
            }), 200

        print(f"\n[Upload] Total images found: {len(all_search_results)}")

        blocked_count = 0
        filtered_results = []
        for r in all_search_results:
            url = r.get('url', '')
            if is_blocked_url(url):
                blocked_count += 1
                continue
            filtered_results.append(r)
        if blocked_count:
            source_notes.append(f"{blocked_count} URL(s) skipped by blocklist")
            print(f"[Upload] Blocklist skipped {blocked_count} URL(s)")

        seen_urls = set()
        unique_results = []
        for result in filtered_results:
            dedup_key = normalize_url_for_dedup(result.get('url'))
            if dedup_key not in seen_urls:
                seen_urls.add(dedup_key)
                unique_results.append(result)

        print(f"[Upload] Unique images after dedup: {len(unique_results)}")
        unique_results = unique_results[:max_candidate_images]
        print(f"[Upload] Candidate images after limit: {len(unique_results)}")

        print("\n[Upload] Starting face matching...")
        matched_images = match_faces(
            user_embedding=user_embedding,
            search_results=unique_results,
            threshold=0.5,
        )

        print(f"[Upload] Found {len(matched_images)} matching images")
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

        # Legacy behavior: dataset/*.jpg were served via /image/. The new
        # pipeline uses remote URLs directly, but we keep this rewrite for
        # any leftover local results.
        for match in matched_images:
            if match['url'].startswith('dataset/'):
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
                'totals': {
                    'raw': len(all_search_results),
                    'after_blocklist': len(filtered_results),
                    'after_dedup': len(unique_results),
                    'matches': len(matched_images),
                },
            },
        }), 200

    except Exception as e:
        print(f"[Upload] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/report', methods=['POST'])
def generate_report():
    """Generate pre-filled Google report link for image removal (legacy)."""
    try:
        data = request.json or {}
        image_url = data.get('image_url')
        image_hash = data.get('image_hash')

        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400

        report_link = generate_report_link(image_url, image_hash)
        return jsonify({'status': 'success', 'report_link': report_link}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/removal-plan', methods=['POST'])
def removal_plan():
    """
    Build a structured, guided takedown plan for a matched image. The
    frontend renders the `steps` list as a wizard.
    """
    try:
        data = request.json or {}
        image_url = data.get('image_url')
        if not image_url:
            return jsonify({'error': 'image_url is required'}), 400

        plan = build_removal_plan(
            image_url=image_url,
            page_url=data.get('page_url') or image_url,
            image_hash=data.get('image_hash') or '',
            user_name=data.get('user_name') or '',
            user_email=data.get('user_email') or '',
        )
        return jsonify({'status': 'success', 'plan': plan}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/verify-match', methods=['POST'])
def verify_match():
    """User confirms if matched image is actually them."""
    try:
        data = request.json or {}
        image_url = data.get('image_url')
        is_match = data.get('is_match')

        print(f"\n[Verify] Image: {image_url}")
        print(f"[Verify] User confirmation: {'This is me' if is_match else 'Not me'}")

        return jsonify({'status': 'success', 'verified': is_match}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Starting Reclaim Backend Server")
    print("=" * 60)
    print("Server running on: http://localhost:5000")
    print("Health check: http://localhost:5000/health")
    print("=" * 60 + "\n")
    app.run(debug=False, port=5000)
