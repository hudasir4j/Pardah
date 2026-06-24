from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import List, Optional

import httpx

from app.config import Settings, get_settings
from app.models.schemas import RawSearchHit

FACECHECK_BASE = "https://facecheck.id"


class FaceCheckClient:
  def __init__(self, settings: Optional[Settings] = None) -> None:
    self.settings = settings or get_settings()

  @property
  def enabled(self) -> bool:
    return bool(self.settings.facecheck_api_token.strip())

  async def search(self, image_paths: List[Path]) -> List[RawSearchHit]:
    if not self.enabled:
      return self._demo_hits()

    # FaceCheck accepts 1–3 images per upload.
    batch = image_paths[:3]
    return await asyncio.to_thread(self._search_sync, batch)

  def _search_sync(self, image_paths: List[Path]) -> List[RawSearchHit]:
    headers = {
      "accept": "application/json",
      "Authorization": self.settings.facecheck_api_token.strip(),
    }
    files = []
    handles = []
    try:
      for p in image_paths:
        fh = open(p, "rb")
        handles.append(fh)
        files.append(("images", (p.name, fh, "image/jpeg")))

      with httpx.Client(timeout=120.0) as client:
        upload = client.post(f"{FACECHECK_BASE}/api/upload_pic", headers=headers, files=files)
        upload.raise_for_status()
        upload_data = upload.json()
        if upload_data.get("error"):
          raise RuntimeError(upload_data.get("message") or "FaceCheck upload failed")

        search_id = upload_data["id_search"]
        payload = {
          "id_search": search_id,
          "with_progress": False,
          "status_only": False,
          "demo": self.settings.facecheck_testing_mode,
        }

        for _ in range(90):
          resp = client.post(f"{FACECHECK_BASE}/api/search", headers=headers, json=payload)
          resp.raise_for_status()
          data = resp.json()
          if data.get("error"):
            raise RuntimeError(data.get("message") or "FaceCheck search failed")
          output = data.get("output") or {}
          items = output.get("items") or []
          if items:
            return self._map_items(items)
          time.sleep(1)
        raise TimeoutError("FaceCheck search timed out")
    finally:
      for fh in handles:
        fh.close()

  def _map_items(self, items: list) -> List[RawSearchHit]:
    hits: List[RawSearchHit] = []
    for item in items:
      url = item.get("url") or item.get("page_url") or ""
      if not url:
        continue
      score = item.get("score")
      thumb = item.get("base64") or item.get("image_base64")
      hits.append(
        RawSearchHit(
          page_url=url,
          image_url=url,
          engine_score=float(score) if score is not None else None,
          thumbnail_b64=thumb,
          source_engine="facecheck",
        )
      )
    return hits

  def _demo_hits(self) -> List[RawSearchHit]:
    return [
      RawSearchHit(
        page_url="https://www.linkedin.com/in/example-profile",
        image_url="https://www.linkedin.com/in/example-profile",
        engine_score=92.0,
        source_engine="facecheck-demo",
        title_hint="LinkedIn Profile — Example",
      ),
      RawSearchHit(
        page_url="https://www.facebook.com/photo/?fbid=123456789",
        image_url="https://www.facebook.com/photo/?fbid=123456789",
        engine_score=88.0,
        source_engine="facecheck-demo",
        title_hint="Facebook Photo",
      ),
      RawSearchHit(
        page_url="https://medium.com/@example/old-blog-post",
        image_url="https://medium.com/@example/old-blog-post",
        engine_score=79.0,
        source_engine="facecheck-demo",
        title_hint="A chapter from before — personal blog",
      ),
    ]
