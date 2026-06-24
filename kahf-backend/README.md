# Kahf Discovery Engine — Backend

FastAPI service for multi-image facial retrieval, DeepFace verification, and ephemeral session privacy.

## Setup

```bash
cd kahf-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
python main.py
```

API docs: http://localhost:8000/docs

## Environment

| Variable | Purpose |
|----------|---------|
| `FACECHECK_API_TOKEN` | FaceCheck.id API token for live web-scale search |
| `FACECHECK_TESTING_MODE` | `true` uses FaceCheck demo mode (no credits) |
| `PIMEYES_API_KEY` | Optional PimEyes scaffold (no public API yet) |
| `CONFIDENCE_THRESHOLD` | DeepFace filter cutoff (default `85`) |
| `SESSION_ENCRYPTION_KEY` | Fernet key for in-memory embedding encryption |
| `SESSION_TTL_MINUTES` | Auto-purge timeout (default `30`) |

Without `FACECHECK_API_TOKEN`, the API returns **demo results** so the frontend can be developed locally.

## Endpoints

- `POST /api/v1/discover` — multi-image upload (min 3), runs search + verification + scraping
- `POST /api/v1/session/{id}/wipe` — immediate session destruction
- `GET /api/v1/health` — service status

## Pipeline

1. Save reference photos to ephemeral session directory
2. Build encrypted in-memory DeepFace embeddings
3. Search FaceCheck.id (and PimEyes when configured)
4. Verify each hit locally with DeepFace (≥85% threshold)
5. Enrich surviving URLs with Playwright metadata scrape
6. Return discovery cards JSON; purge on wipe or TTL

## Privacy

- Biometric embeddings encrypted in memory (Fernet)
- No persistent database in Phase 0 prototype
- Session wipe deletes temp files and clears memory
- Supabase/S3 hooks reserved for Phase 1 deployment
