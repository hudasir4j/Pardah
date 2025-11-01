# Pardah

A digital privacy tool helping hijabis remove unwanted images from the web.

## The Problem
It is often discouraging Hijabis often have photos online of them without their hijab that they want removed. This product streamlines the process to get them off the internet

## How It Works
1. Upload a photo of yourself (with hijab)
2. We search the web for similar images
3. We identify which ones are you without your hijab
4. One-click report to Google for removal

## Team
- Frontend: Aleesha Ilahi and Sanaa Asif
- Backend: Huda Siraj and Zoya Khan

## Setup Instructions
See below to deploy Pardah on your computer

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
# You can tun Pardah at http://localhost:8000 in your browser
```

## APIs & Tools Used
- Bing Image Search API
- Face Recognition (HuggingFace)
- Flask (Backend)
- Vanilla JavaScript (Frontend)