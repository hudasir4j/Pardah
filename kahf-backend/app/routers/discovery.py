from __future__ import annotations

import asyncio
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.models.schemas import (
  DiscoveryResponse,
  DiscoveryResult,
  MatchTier,
  SessionStatus,
  SessionSummary,
  WipeResponse,
)
from app.services.facecheck import FaceCheckClient
from app.services.pimeyes import PimEyesClient
from app.services.scraper import enrich_url
from app.services.session_store import get_session_store
from app.services.verification import VerificationService

router = APIRouter(prefix="/api/v1", tags=["discovery"])


def _tier_label(score: float, threshold: float) -> MatchTier:
  if score >= threshold:
    return MatchTier.HIGH
  if score >= threshold - 10:
    return MatchTier.MEDIUM
  return MatchTier.LOW


@router.post("/discover", response_model=DiscoveryResponse)
async def discover(files: List[UploadFile] = File(...)) -> DiscoveryResponse:
  settings = get_settings()
  store = get_session_store()

  if len(files) < settings.min_reference_photos:
    raise HTTPException(
      status_code=400,
      detail=f"Please upload at least {settings.min_reference_photos} reference photos.",
    )
  if len(files) > settings.max_reference_photos:
    raise HTTPException(
      status_code=400,
      detail=f"Maximum {settings.max_reference_photos} reference photos allowed.",
    )

  session = store.create_session()
  session.status = "processing"
  session_dir = store.session_dir(session.session_id)

  saved_paths: List[Path] = []
  for upload in files:
    if not upload.content_type or not upload.content_type.startswith("image/"):
      raise HTTPException(status_code=400, detail="All uploads must be image files.")
    suffix = Path(upload.filename or "photo.jpg").suffix or ".jpg"
    dest = session_dir / f"{uuid.uuid4().hex}{suffix}"
    data = await upload.read()
    dest.write_bytes(data)
    saved_paths.append(dest)
    session.reference_paths.append(dest)

  verifier = VerificationService(settings)
  try:
    ref_embeddings = await asyncio.to_thread(verifier.build_reference_embeddings, saved_paths)
    store.store_embeddings(session.session_id, ref_embeddings)
  except Exception as exc:
    store.wipe_session(session.session_id)
    raise HTTPException(status_code=422, detail=f"Could not build biometric profile: {exc}") from exc

  engines_used: List[str] = []
  facecheck = FaceCheckClient(settings)
  pimeyes = PimEyesClient(settings)

  raw_hits = []
  fc_hits = await facecheck.search(saved_paths)
  if fc_hits:
    engines_used.append("facecheck" if facecheck.enabled else "facecheck-demo")
    raw_hits.extend(fc_hits)

  pm_hits = await pimeyes.search(saved_paths)
  if pm_hits:
    engines_used.append("pimeyes")
    raw_hits.extend(pm_hits)

  seen_urls = set()
  unique_hits = []
  for hit in raw_hits:
    key = hit.page_url.rstrip("/")
    if key in seen_urls:
      continue
    seen_urls.add(key)
    unique_hits.append(hit)

  results: List[DiscoveryResult] = []
  for hit in unique_hits:
    temp_path = await verifier.download_hit_image(hit.image_url, hit.thumbnail_b64)
    confidence = hit.engine_score or 0.0
    verified = False

    if temp_path:
      try:
        deepface_score, passed = await asyncio.to_thread(
          verifier.verify_hit, temp_path, ref_embeddings
        )
        confidence = deepface_score
        verified = passed
      finally:
        try:
          temp_path.unlink(missing_ok=True)
        except OSError:
          pass
    elif hit.engine_score is not None and hit.engine_score >= settings.confidence_threshold:
      verified = True
      confidence = hit.engine_score
    else:
      continue

    if not verified:
      continue

    meta = await enrich_url(hit.page_url, settings)
    tier = _tier_label(confidence, settings.confidence_threshold)

    results.append(
      DiscoveryResult(
        id=secrets.token_hex(8),
        image_url=hit.image_url,
        thumbnail_url=hit.image_url if hit.thumbnail_b64 else None,
        page_url=hit.page_url,
        confidence_score=round(confidence, 1),
        match_tier=tier,
        platform=meta.platform or "Unknown",
        page_title=meta.page_title or hit.title_hint,
        date_published=meta.date_published,
        context_snippet=meta.context_snippet,
        source_engine=hit.source_engine,
        scraped=meta.scraped,
      )
    )

  results.sort(key=lambda r: r.confidence_score, reverse=True)
  session.results = [r.model_dump() for r in results]
  session.engines_used = engines_used
  session.status = "complete"

  message = None
  if not facecheck.enabled:
    message = (
      "Running in demo mode — set FACECHECK_API_TOKEN in backend/.env for live searches."
    )

  return DiscoveryResponse(
    session=SessionSummary(
      session_id=session.session_id,
      status=SessionStatus.COMPLETE,
      created_at=session.created_at,
      expires_at=session.expires_at,
      reference_count=len(saved_paths),
      result_count=len(results),
    ),
    results=results,
    engines_used=engines_used,
    message=message,
  )


@router.post("/session/{session_id}/wipe", response_model=WipeResponse)
async def wipe_session(session_id: str) -> WipeResponse:
  store = get_session_store()
  wiped = store.wipe_session(session_id)
  if not wiped:
    raise HTTPException(status_code=404, detail="Session not found or already expired.")
  return WipeResponse(
    session_id=session_id,
    wiped=True,
    message="Your session, reference photos, and discovery results have been permanently deleted.",
  )


@router.get("/health")
async def health() -> dict:
  settings = get_settings()
  return {
    "status": "ok",
    "service": "kahf-discovery-engine",
    "confidence_threshold": settings.confidence_threshold,
    "facecheck_configured": bool(settings.facecheck_api_token.strip()),
    "pimeyes_configured": bool(settings.pimeyes_api_key.strip()),
  }
