"""
Face embedding + matching.

Improvements over the original:
- Preloads the Facenet512 model once at import time, so per-image work skips
  model initialization.
- Uses a shared HTTP session (browser UA, retries) and resolves social-media
  crawler URLs to their real CDN image URL.
- Parallelizes candidate processing with a ThreadPoolExecutor; each worker
  writes to its own tempfile (the old code shared `/tmp/temp_face.jpg`,
  which serialized everything).
- Downscales images before detection (faster, less memory).
- Reuses already-downloaded bytes for SHA-256 hashing instead of issuing a
  second HTTP request.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image
from deepface import DeepFace

from http_client import fetch_bytes
from social_resolver import fetch_image_bytes_with_resolve


# Preload model once so DeepFace.represent doesn't re-init per call.
try:
    _MODEL = DeepFace.build_model("Facenet512")
    print("[Face] Facenet512 model preloaded")
except Exception as _e:
    _MODEL = None
    print(f"[Face] Warning: model preload failed ({_e}); will build on demand")

# Detector backend: opencv is ~3-5x faster than retinaface/mtcnn with
# acceptable accuracy for our similarity threshold.
_DETECTOR_BACKEND = os.environ.get("FACE_DETECTOR_BACKEND", "opencv")

# Max edge for images passed to DeepFace. Larger images waste detector time.
_MAX_IMAGE_EDGE = 1024

# I/O-bound; we can afford more workers than CPU cores.
_MAX_WORKERS = int(os.environ.get("FACE_MATCH_WORKERS", "6"))

_model_lock = threading.Lock()


def _prepare_image_file(image_bytes: bytes, out_path: str) -> bool:
    """Decode, downscale, and re-encode as JPEG. Returns False on failure."""
    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        elif img.mode == "L":
            img = img.convert("RGB")
        w, h = img.size
        longest = max(w, h)
        if longest > _MAX_IMAGE_EDGE:
            scale = _MAX_IMAGE_EDGE / float(longest)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        img.save(out_path, format="JPEG", quality=90)
        return True
    except Exception as e:
        print(f"[Face] Could not decode image bytes: {e}")
        return False


def _represent(image_path: str, enforce_detection: bool = True):
    """Thread-safe wrapper around DeepFace.represent."""
    # DeepFace caches models via a module-level dict; calls from multiple
    # threads concurrently into Keras can be flaky. A coarse lock around the
    # inference call keeps us correct with little real-world cost because
    # HTTP I/O and image decoding still run in parallel.
    with _model_lock:
        return DeepFace.represent(
            img_path=image_path,
            model_name="Facenet512",
            detector_backend=_DETECTOR_BACKEND,
            enforce_detection=enforce_detection,
        )


def extract_face_embedding(image_path: str) -> Optional[np.ndarray]:
    """Extract a 512-dim face embedding from a local image file."""
    try:
        print(f"[Face] Extracting embedding from: {image_path}")
        result = _represent(image_path, enforce_detection=True)
        if not result:
            print("[Face] No face found in image")
            return None
        embedding = np.array(result[0]["embedding"])
        print("[Face] Embedding extracted successfully (512-dim vector)")
        return embedding
    except Exception as e:
        print(f"[Face] Error extracting embedding: {e}")
        return None


def _embedding_from_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    """Write bytes to a per-worker temp file, extract embedding, clean up."""
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp_path = tmp.name
    tmp.close()
    try:
        if not _prepare_image_file(image_bytes, tmp_path):
            return None
        result = _represent(tmp_path, enforce_detection=True)
        if not result:
            return None
        return np.array(result[0]["embedding"])
    except Exception as e:
        # Quiet common "no face" case (DeepFace raises ValueError for it).
        msg = str(e)
        if "Face could not be detected" in msg:
            return None
        print(f"[Face] Embedding error: {msg}")
        return None
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def extract_face_embedding_from_url(image_url: str) -> Optional[np.ndarray]:
    """Fetch (with social-crawler resolution), then embed. Used for ad-hoc calls."""
    try:
        if image_url.startswith("http"):
            data = fetch_image_bytes_with_resolve(image_url)
            if data is None:
                return None
        else:
            with open(image_url, "rb") as f:
                data = f.read()
        return _embedding_from_bytes(data)
    except Exception as e:
        print(f"[Face] Error extracting face from URL {image_url}: {e}")
        return None


def compare_faces(
    user_embedding: np.ndarray, search_embedding: np.ndarray, threshold: float = 0.6
) -> Tuple[bool, float]:
    """Cosine-distance comparison. Lower threshold is stricter."""
    try:
        user_norm = user_embedding / np.linalg.norm(user_embedding)
        search_norm = search_embedding / np.linalg.norm(search_embedding)
        cosine_sim = float(np.dot(user_norm, search_norm))
        distance = 1.0 - cosine_sim
        return distance < threshold, distance
    except Exception as e:
        print(f"[Face] Error comparing faces: {e}")
        return False, 1.0


def _load_bytes(image_source: str) -> Optional[bytes]:
    """Unified byte loader - handles URLs (with social resolution) and local paths."""
    try:
        if image_source.startswith("http"):
            return fetch_image_bytes_with_resolve(image_source)
        with open(image_source, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"[Face] Fetch error for {image_source}: {e}")
        return None


def _process_one(
    idx: int,
    total: int,
    user_embedding: np.ndarray,
    result: Dict,
    threshold: float,
) -> Optional[Dict]:
    image_url = result.get("url", "")
    title = result.get("title", "Unknown")
    print(f"[Face Matching] Processing {idx + 1}/{total}: {title[:60]}")

    data = _load_bytes(image_url)
    if not data:
        print("  ✗ Could not fetch image")
        return None

    embedding = _embedding_from_bytes(data)
    if embedding is None:
        print("  ✗ No face detected")
        return None

    is_match, distance = compare_faces(user_embedding, embedding, threshold)
    similarity = float(1 - (distance / 2))
    if not is_match:
        print(f"  ✗ Not a match (distance: {distance:.3f}, needed: < {threshold})")
        return None

    img_hash = hashlib.sha256(data).hexdigest()
    print(f"  ✓ MATCH FOUND! Distance: {distance:.3f}, Similarity: {similarity:.1%}")
    return {
        "url": image_url,
        "page_url": result.get("page_url", image_url),
        "title": title,
        "source": result.get("source", "Unknown"),
        "similarity_score": similarity,
        "distance": float(distance),
        "image_hash": img_hash,
    }


def match_faces(
    user_embedding: np.ndarray,
    search_results: List[Dict],
    threshold: float = 0.5,
) -> List[Dict]:
    """
    Compare the user's face against each candidate. I/O (download) and
    CPU-bound embedding extraction run on a thread pool; DeepFace inference
    itself is serialized by `_model_lock` to play nice with Keras.
    """
    total = len(search_results)
    print(f"\n[Face Matching] Starting to match {total} images with {_MAX_WORKERS} workers...")
    print(f"[Face Matching] Threshold: {threshold} (lower = stricter matching)")

    matches: List[Dict] = []
    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
        futures = {
            pool.submit(_process_one, i, total, user_embedding, res, threshold): i
            for i, res in enumerate(search_results)
        }
        for fut in as_completed(futures):
            try:
                m = fut.result()
            except Exception as e:
                print(f"[Face Matching] Worker error: {e}")
                continue
            if m is not None:
                matches.append(m)

    matches.sort(key=lambda x: x["similarity_score"], reverse=True)
    print(f"\n[Face Matching] Complete! Found {len(matches)} matching images\n")
    return matches


def get_image_hash(image_url: str) -> Optional[str]:
    """Kept for backwards compatibility; new code reuses bytes directly."""
    try:
        data = _load_bytes(image_url)
        if not data:
            return None
        return hashlib.sha256(data).hexdigest()
    except Exception as e:
        print(f"[Face] Error hashing image: {e}")
        return None
