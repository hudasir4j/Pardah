from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from app.config import Settings, get_settings
from app.models.schemas import RawSearchHit


class PimEyesClient:
  """
  PimEyes does not publish a stable public API. This client is a scaffold:
  when PIMEYES_API_KEY is set, POST images to a configurable endpoint.
  Otherwise it returns nothing and the pipeline relies on FaceCheck.
  """

  def __init__(self, settings: Optional[Settings] = None) -> None:
    self.settings = settings or get_settings()

  @property
  def enabled(self) -> bool:
    return bool(self.settings.pimeyes_api_key.strip())

  async def search(self, image_paths: List[Path]) -> List[RawSearchHit]:
    if not self.enabled:
      return []
    # Placeholder for future PimEyes partner API integration.
    return []
