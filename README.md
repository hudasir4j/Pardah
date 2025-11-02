# Pardah
Revolutionary privacy technology empowering hijabis through an accessible way to erase digital footprint and protect modesty online.

## The Problem
Hijabis often have photos online of them without their hijab that they want removed. This product helps them find and report those images.

## How It Works
1. Upload a photo of yourself (with hijab) & provide keywords to find your pictures
2. We search the web for pictures
3. We identify which ones are you without your hijab
4. Streamlined image reporting!

## Team
- Backend: Huda Siraj and Zoya Khan
- Frontend: Sanaa Asif and Aleesha Ilahi

## Setup Instructions
See below for how to run locally.

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

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
  - Requests: HTTP library for downloading images from URLs
  - Werkzeug: Secure filename handling and file upload management
  - Hashlib: SHA256 image hashing for reporting
