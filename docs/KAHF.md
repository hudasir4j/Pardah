# Kahf Discovery Engine — Phase 0

Kahf helps women safely discover and manage pre-transition digital footprints through high-precision facial retrieval and an empathetic editorial interface.

## Repository layout

| Path | Stack | Role |
|------|-------|------|
| `kahf-backend/` | FastAPI, DeepFace, Playwright | Retrieval pipeline, verification, scraping, session privacy |
| `kahf-app/` | Next.js, Tailwind | Upload UI, discovery dashboard, wipe session |
| `prd.md` | — | Product requirements |

## Quick start

**Terminal 1 — backend**
```bash
cd kahf-backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
python main.py
```

**Terminal 2 — frontend**
```bash
cd kahf-app
npm install
cp .env.example .env.local
npm run dev
```

## Phase 0 scope

- Multi-image upload (3–5 photos)
- FaceCheck.id API orchestration (+ PimEyes scaffold)
- DeepFace local verification (85% threshold)
- Playwright page metadata enrichment
- Encrypted in-memory embeddings, 30-min TTL, wipe endpoint
- Editorial cream/pastel UI with discovery cards

## Not yet in Phase 0

- Supabase session persistence (env hooks only)
- S3 ephemeral storage (local temp dir used instead)
- PimEyes live API (no stable public API)

See `kahf-backend/README.md` and `kahf-app/README.md` for details.
