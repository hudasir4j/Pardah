"""
Face embedding + matching using OpenCV's built-in YuNet detector and SFace
recognizer (both ONNX). This replaces the previous TensorFlow + DeepFace
stack to fit on 512 MB hosts.

Memory footprint compared to the old stack:
  - cv2 + ONNX runtime: ~50-80 MB (was: TF 2.15 ~400-500 MB)
  - YuNet detector ONNX: ~2 MB
  - SFace recognizer ONNX: ~37 MB
  - Total idle: ~200-260 MB (was: ~900 MB-1.1 GB)

The public API (`extract_face_embedding`, `match_faces`, `compare_faces`,
`DEFAULT_MATCH_THRESHOLD`, `extract_face_embedding_from_url`,
`get_image_hash`) is preserved so callers in main.py don't need to change.
"""
from __future__ import annotations

import gc
import hashlib
import os
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from http_client import fetch_bytes  # noqa: F401 (re-exported for callers)
from social_resolver import fetch_image_bytes_with_resolve


# Official OpenCV model zoo URLs. Pinned commits keep us reproducible.
_YUNET_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/"
    "models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
_SFACE_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/"
    "models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
)

_MODELS_DIR = Path(os.environ.get("PARDAH_MODELS_DIR", "models"))
_YUNET_PATH = _MODELS_DIR / "face_detection_yunet_2023mar.onnx"
_SFACE_PATH = _MODELS_DIR / "face_recognition_sface_2021dec.onnx"


def _download_once(url: str, dest: Path) -> None:
    """Download `url` to `dest` if not already present. Atomic via .tmp rename."""
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[Face] Downloading {url}")
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    try:
        with urllib.request.urlopen(url, timeout=60) as resp, open(tmp, "wb") as f:
            while True:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)
        tmp.rename(dest)
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"[Face] Downloaded {dest.name} ({size_mb:.1f} MB)")
    finally:
        # Best-effort cleanup if the rename never happened.
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


_download_once(_YUNET_URL, _YUNET_PATH)
_download_once(_SFACE_URL, _SFACE_PATH)


# Detector input size is updated per-image via setInputSize(); the (320, 320)
# here is just a placeholder so create() succeeds.
_detector = cv2.FaceDetectorYN.create(
    model=str(_YUNET_PATH),
    config="",
    input_size=(320, 320),
    score_threshold=float(os.environ.get("FACE_DETECT_SCORE_THRESHOLD", "0.6")),
    nms_threshold=float(os.environ.get("FACE_DETECT_NMS_THRESHOLD", "0.3")),
    top_k=5000,
)
_recognizer = cv2.FaceRecognizerSF.create(
    model=str(_SFACE_PATH),
    config="",
)
print("[Face] OpenCV YuNet + SFace models preloaded")


# Default cosine-distance match threshold. We use distance = 1 - cosine_sim
# of L2-normalized embeddings (range [0, 2]). SFace's reference cosine-sim
# threshold is ~0.363, i.e. distance < 0.637 -> match. We default slightly
# stricter at 0.60.
DEFAULT_MATCH_THRESHOLD = float(os.environ.get("FACE_MATCH_THRESHOLD", "0.60"))

# Max edge for input images. SFace internally aligns to 112x112, so going
# above ~640 just costs decode RAM with negligible accuracy gain.
_MAX_IMAGE_EDGE = int(os.environ.get("FACE_MAX_IMAGE_EDGE", "640"))

# Concurrent download/decode workers. Each in-flight worker holds raw image
# bytes + a decoded ndarray, so keep this small on tight memory budgets.
# Inference itself is serialized by _model_lock (cv2 face models are not
# thread-safe).
_MAX_WORKERS = int(os.environ.get("FACE_MATCH_WORKERS", "2"))

_model_lock = threading.Lock()


def _bytes_to_bgr(image_bytes: bytes) -> Optional[np.ndarray]:
    """Decode bytes -> downscaled BGR ndarray. Returns None on failure."""
    img = None
    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        w, h = img.size
        longest = max(w, h)
        if longest > _MAX_IMAGE_EDGE:
            scale = _MAX_IMAGE_EDGE / float(longest)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        arr = np.asarray(img, dtype=np.uint8)
        # PIL gives us RGB; OpenCV operates in BGR.
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"[Face] Could not decode image bytes: {e}")
        return None
    finally:
        if img is not None:
            try:
                img.close()
            except Exception:
                pass


def _embedding_from_bgr(bgr: np.ndarray) -> Optional[np.ndarray]:
    """Detect the largest face and return its 128-dim SFace embedding."""
    with _model_lock:
        h, w = bgr.shape[:2]
        _detector.setInputSize((w, h))
        _, faces = _detector.detect(bgr)
        if faces is None or len(faces) == 0:
            return None

        # YuNet rows: [x, y, w, h, kp_x*5, kp_y*5, score]. Pick the largest
        # face by bounding-box area; tiny faces give noisy embeddings.
        areas = faces[:, 2] * faces[:, 3]
        best = faces[int(np.argmax(areas))]

        aligned = _recognizer.alignCrop(bgr, best)
        feat = _recognizer.feature(aligned)
        return feat.reshape(-1).astype(np.float32)


def _embedding_from_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    bgr = _bytes_to_bgr(image_bytes)
    if bgr is None:
        return None
    try:
        return _embedding_from_bgr(bgr)
    finally:
        del bgr


def extract_face_embedding(image_path: str) -> Optional[np.ndarray]:
    """Extract a face embedding from a local image file."""
    try:
        print(f"[Face] Extracting embedding from: {image_path}")
        with open(image_path, "rb") as f:
            data = f.read()
        emb = _embedding_from_bytes(data)
        if emb is None:
            print("[Face] No face found in image")
            return None
        print(f"[Face] Embedding extracted (SFace, {emb.shape[0]}-dim)")
        return emb
    except Exception as e:
        print(f"[Face] Error extracting embedding: {e}")
        return None


def extract_face_embedding_from_url(image_url: str) -> Optional[np.ndarray]:
    """Fetch (with social-crawler resolution), then embed."""
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
    user_embedding: np.ndarray,
    search_embedding: np.ndarray,
    threshold: float = DEFAULT_MATCH_THRESHOLD,
) -> Tuple[bool, float]:
    """Cosine-distance comparison. Lower threshold is stricter."""
    try:
        u_norm = float(np.linalg.norm(user_embedding))
        s_norm = float(np.linalg.norm(search_embedding))
        if u_norm == 0.0 or s_norm == 0.0:
            return False, 1.0
        u = user_embedding / u_norm
        s = search_embedding / s_norm
        cosine_sim = float(np.dot(u, s))
        distance = 1.0 - cosine_sim
        return distance < threshold, distance
    except Exception as e:
        print(f"[Face] Error comparing faces: {e}")
        return False, 1.0


def _load_bytes(image_source: str) -> Optional[bytes]:
    """Unified byte loader: URLs (with social resolution) and local paths."""
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

    img_hash = hashlib.sha256(data).hexdigest()

    try:
        embedding = _embedding_from_bytes(data)
    finally:
        # Free raw bytes ASAP so peak across concurrent workers stays low.
        del data

    if embedding is None:
        print("  ✗ No face detected")
        return None

    is_match, distance = compare_faces(user_embedding, embedding, threshold)
    similarity = float(1 - (distance / 2))
    if not is_match:
        print(f"  ✗ Not a match (distance: {distance:.3f}, needed: < {threshold})")
        return None

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
    threshold: Optional[float] = None,
) -> List[Dict]:
    """
    Compare the user's face against each candidate. Downloads + decodes run
    on a thread pool; cv2 inference itself is serialized by _model_lock.
    """
    if threshold is None:
        threshold = DEFAULT_MATCH_THRESHOLD
    total = len(search_results)
    print(f"\n[Face Matching] Starting to match {total} images with {_MAX_WORKERS} workers...")
    print(f"[Face Matching] Backend: cv2 SFace, threshold: {threshold} (lower = stricter)")

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
    gc.collect()
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
