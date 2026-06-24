from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import discovery
from app.services.session_store import get_session_store

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
  store = get_session_store()

  async def _janitor() -> None:
    while True:
      store.purge_expired()
      await asyncio.sleep(60)

  task = asyncio.create_task(_janitor())
  yield
  task.cancel()


app = FastAPI(
  title="Kahf Discovery Engine",
  description="High-precision facial retrieval with zero-retention session privacy.",
  version="0.1.0",
  lifespan=lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(discovery.router)


@app.get("/")
async def root() -> dict:
  return {"service": "kahf-discovery-engine", "docs": "/docs"}


if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
