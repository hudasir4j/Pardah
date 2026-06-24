from __future__ import annotations

import base64
import json
import secrets
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from cryptography.fernet import Fernet, InvalidToken

from app.config import Settings, get_settings


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _fernet(settings: Settings) -> Fernet:
    key = settings.session_encryption_key.strip()
    if not key:
        # Ephemeral dev key — regenerated each process; fine for local prototype.
        key = Fernet.generate_key().decode()
    return Fernet(key.encode() if isinstance(key, str) else key)


@dataclass
class SessionPayload:
    session_id: str
    created_at: datetime
    expires_at: datetime
    status: str
    reference_paths: List[Path] = field(default_factory=list)
    encrypted_embeddings_blob: Optional[bytes] = None
    results: List[dict] = field(default_factory=list)
    engines_used: List[str] = field(default_factory=list)
    error: Optional[str] = None


class SessionStore:
    """In-memory encrypted session store. No biometric data persists to disk."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._sessions: Dict[str, SessionPayload] = {}
        self._lock = threading.RLock()
        self._fernet = _fernet(self.settings)
        self._temp_root = Path("kahf-temp")
        self._temp_root.mkdir(exist_ok=True)

    def create_session(self) -> SessionPayload:
        session_id = secrets.token_urlsafe(24)
        now = _utcnow()
        expires = now + timedelta(minutes=self.settings.session_ttl_minutes)
        payload = SessionPayload(
            session_id=session_id,
            created_at=now,
            expires_at=expires,
            status="created",
        )
        session_dir = self._temp_root / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self._sessions[session_id] = payload
        return payload

    def get(self, session_id: str) -> Optional[SessionPayload]:
        self.purge_expired()
        with self._lock:
            return self._sessions.get(session_id)

    def session_dir(self, session_id: str) -> Path:
        return self._temp_root / session_id

    def store_embeddings(self, session_id: str, embeddings: List[List[float]]) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return
            raw = json.dumps(embeddings).encode()
            session.encrypted_embeddings_blob = self._fernet.encrypt(raw)

    def load_embeddings(self, session_id: str) -> Optional[List[List[float]]]:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.encrypted_embeddings_blob:
                return None
            try:
                raw = self._fernet.decrypt(session.encrypted_embeddings_blob)
                return json.loads(raw.decode())
            except (InvalidToken, json.JSONDecodeError):
                return None

    def wipe_session(self, session_id: str) -> bool:
        with self._lock:
            session = self._sessions.pop(session_id, None)
        if not session:
            return False
        session_dir = self._temp_root / session_id
        if session_dir.exists():
            for p in session_dir.rglob("*"):
                if p.is_file():
                    try:
                        p.unlink()
                    except OSError:
                        pass
            try:
                session_dir.rmdir()
            except OSError:
                pass
        session.reference_paths.clear()
        session.encrypted_embeddings_blob = None
        session.results.clear()
        session.status = "wiped"
        return True

    def purge_expired(self) -> int:
        now = _utcnow()
        expired_ids = []
        with self._lock:
            for sid, payload in self._sessions.items():
                if payload.expires_at <= now:
                    expired_ids.append(sid)
        count = 0
        for sid in expired_ids:
            if self.wipe_session(sid):
                count += 1
        return count


_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
