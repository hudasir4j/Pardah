from __future__ import annotations

import base64
import re
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import httpx
from deepface import DeepFace

from app.config import Settings, get_settings

PLATFORM_RULES = [
  (r"linkedin\.com", "LinkedIn"),
  (r"facebook\.com|fbcdn\.net", "Facebook"),
  (r"instagram\.com|cdninstagram", "Instagram"),
  (r"twitter\.com|x\.com|twimg\.com", "X (Twitter)"),
  (r"tiktok\.com", "TikTok"),
  (r"medium\.com", "Personal Blog"),
  (r"blogspot\.|wordpress\.com", "Personal Blog"),
  (r"news\.|\.news", "News"),
  (r"archive\.org", "Web Archive"),
]


def detect_platform(url: str) -> str:
  lower = (url or "").lower()
  for pattern, label in PLATFORM_RULES:
    if re.search(pattern, lower):
      return label
  host = urlparse(url).hostname or ""
  if host:
    return host.replace("www.", "")
  return "Unknown"


def _tier(score: float, threshold: float) -> str:
  if score >= threshold:
    return "high"
  if score >= threshold - 10:
    return "medium"
  return "low"


class VerificationService:
  def __init__(self, settings: Optional[Settings] = None) -> None:
    self.settings = settings or get_settings()
    self.model = self.settings.deepface_model

  def build_reference_embeddings(self, image_paths: List[Path]) -> List[List[float]]:
    embeddings: List[List[float]] = []
    for path in image_paths:
      rep = DeepFace.represent(
        img_path=str(path),
        model_name=self.model,
        enforce_detection=False,
      )
      if rep:
        embeddings.append(rep[0]["embedding"])
    return embeddings

  def verify_hit(
    self,
    hit_image_path: Path,
    reference_embeddings: List[List[float]],
  ) -> Tuple[float, bool]:
    try:
      rep = DeepFace.represent(
        img_path=str(hit_image_path),
        model_name=self.model,
        enforce_detection=False,
      )
    except Exception:
      return 0.0, False

    if not rep or not reference_embeddings:
      return 0.0, False

    candidate = rep[0]["embedding"]
    best_distance = min(_cosine_distance(candidate, ref) for ref in reference_embeddings)

    # Cosine distance [0,2] -> similarity percent
    similarity = max(0.0, min(100.0, (1.0 - best_distance / 2.0) * 100.0))
    passed = similarity >= self.settings.confidence_threshold
    return similarity, passed

  async def download_hit_image(
    self,
    hit_url: str,
    thumbnail_b64: Optional[str] = None,
  ) -> Optional[Path]:
    if thumbnail_b64:
      try:
        data = base64.b64decode(thumbnail_b64)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tmp.write(data)
        tmp.close()
        return Path(tmp.name)
      except Exception:
        pass

    if not hit_url.startswith("http"):
      return None

    try:
      async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        resp = await client.get(hit_url)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type and not hit_url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
          return None
        suffix = ".jpg"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(resp.content)
        tmp.close()
        return Path(tmp.name)
    except Exception:
      return None


def _cosine_distance(a: List[float], b: List[float]) -> float:
  import numpy as np

  va = np.array(a, dtype=float)
  vb = np.array(b, dtype=float)
  na = np.linalg.norm(va)
  nb = np.linalg.norm(vb)
  if na == 0 or nb == 0:
    return 2.0
  sim = float(np.dot(va / na, vb / nb))
  return 1.0 - sim
