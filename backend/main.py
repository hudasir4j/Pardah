from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from search_images import search_images_bing
from face_recognition_module import extract_face_embedding, match_faces
from report_generator import generate_report_link
import threading

