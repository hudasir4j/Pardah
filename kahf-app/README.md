# Kahf — Phase 0 Frontend

Next.js (App Router) + Tailwind CSS editorial UI for the Kahf Discovery Engine.

## Setup

```bash
cd kahf-app
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000

Ensure the backend is running at `http://localhost:8000` (see `../kahf-backend/README.md`).

## Design

- **Cream background** `#F9F6F0`, charcoal text `#2A2A2A`
- **Serif headings** (Playfair Display), **sans body** (DM Sans)
- Pastel sage, blue, yellow accents; terracotta CTAs
- Masonry discovery cards with soft pills and rounded corners

## Flow

1. Upload 3–5 reference photos
2. Loading state with empathetic copy
3. Discovery grid with confidence tags and Review Link buttons
4. Wipe session — calls backend purge endpoint
