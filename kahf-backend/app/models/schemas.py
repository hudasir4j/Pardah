from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MatchTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReferencePhotoMeta(BaseModel):
    filename: str
    size_bytes: int


class DiscoveryResult(BaseModel):
    id: str
    image_url: str
    thumbnail_url: Optional[str] = None
    page_url: str
    confidence_score: float = Field(ge=0, le=100)
    match_tier: MatchTier
    platform: str
    page_title: Optional[str] = None
    date_published: Optional[str] = None
    context_snippet: Optional[str] = None
    source_engine: str
    scraped: bool = False


class SessionStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETE = "complete"
    WIPED = "wiped"
    EXPIRED = "expired"
    ERROR = "error"


class SessionSummary(BaseModel):
    session_id: str
    status: SessionStatus
    created_at: datetime
    expires_at: datetime
    reference_count: int = 0
    result_count: int = 0


class DiscoveryResponse(BaseModel):
    session: SessionSummary
    results: List[DiscoveryResult]
    engines_used: List[str]
    message: Optional[str] = None


class WipeResponse(BaseModel):
    session_id: str
    wiped: bool
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class RawSearchHit(BaseModel):
    page_url: str
    image_url: str
    engine_score: Optional[float] = None
    thumbnail_b64: Optional[str] = None
    source_engine: str
    title_hint: Optional[str] = None
