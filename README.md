# Pardah
Revolutionary privacy technology empowering hijabis through an accessible way to erase digital footprint and protect modesty online.

## The Problem
Hijabis often have photos online of them without their hijab that they want removed. This product helps them find and report those images.

## How It Works
1. Upload a photo of yourself (with hijab) & provide keywords to find your pictures
2. We search **Bing Images**, **Google Images** (optional SerpApi key), and **DuckDuckGo Images**
3. We identify which ones are you (face matching)
4. Streamlined image reporting!

## Team
- Backend: Huda Siraj and Zoya Khan
- Frontend: Sanaa Asif and Aleesha Ilahi

## Setup Instructions
See below for how to run locally.

### Backend Setup
Use a **virtual environment** so the backend uses the same Python that has TensorFlow 2.15:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
# TensorFlow 2.15 includes Keras; remove standalone keras so tensorflow.keras works
pip uninstall keras -y
# Optional: copy .env.example to .env and set SERPAPI_API_KEY for Google Images
# and test limits (IMAGES_PER_SOURCE, MAX_SEARCH_QUERIES, etc.)
python main.py
```

Always run the server with the venv activated (`source venv/bin/activate` then `python main.py`). If you see:
- **`No module named 'tensorflow.keras'`** — The standalone `keras` package (installed by deepface) can conflict. Uninstall it so TensorFlow’s bundled Keras is used: `pip uninstall keras -y`, then run `python main.py` again.
- **`AttributeError: ... register_load_context_function`** — Uninstall tf_keras and use only TensorFlow 2.15: `pip uninstall tf-keras -y && pip install "tensorflow>=2.15.0,<2.16"`.

### Frontend Setup
```bash
cd frontend
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

## Stack:

Frontend Stack
* React (v19.2): Builds the UI with reusable components and hooks
* Axios: Sends and receives data from the Flask backend
* React Hooks: useState for managing component state
* CSS3: Custom responsive styling
  
Backend Stack
* Logistics
  - Flask: Python web framework for creating REST API endpoints
  - Flask-CORS: Enables cross-origin requests from React frontend
  - Python-dotenv: Environment variable management
* Libraries
  - DeepFace: AI library for facial recognition using FaceNet512 model
  - OpenCV: Image processing and computer vision operations
  - Pillow (PIL): Image manipulation and format conversion
  - NumPy: Mathematical operations on face embeddings (512-dimensional vectors)
  - Bing Image Downloader: Web scraping tool to search and download images
  - SerpApi (optional): Google Images search when `SERPAPI_API_KEY` is set in `.env`
  - DuckDuckGo Search: DuckDuckGo Images search (no API key)
  - Requests: HTTP library for downloading images from URLs
  - Werkzeug: Secure filename handling and file upload management
  - Hashlib: SHA256 image hashing for reporting
