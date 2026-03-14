"""
main.py
───────
FastAPI application entry-point for the **Environmental Command Center**.

Responsibilities:
    • Creates the FastAPI app with metadata & CORS middleware.
    • Auto-creates database tables on first startup.
    • Registers the background scheduler (APScheduler).
    • Mounts air-quality and noise-pollution routers.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import async_engine
from app.routes.air import router as air_router
from app.routes.noise import router as noise_router
from app.routes.sound import router as sound_router
from app.scheduler.jobs import start_scheduler, stop_scheduler

# ── Logging ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ──────────────────────────────────────
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    On startup:
        1. Create all tables if they don't exist.
        2. Start the APScheduler background jobs.

    On shutdown:
        1. Stop the scheduler.
        2. Dispose of the database engine.
    """
    # Startup — attempt to create tables; warn but don't crash if DB is unavailable.
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables ensured.")
    except Exception as exc:
        logger.warning(
            "Could not connect to the database on startup: %s\n"
            "The server will start, but DB-dependent endpoints will fail until "
            "PostgreSQL is reachable. Check your DATABASE_URL in .env.",
            exc,
        )

    start_scheduler()
    logger.info("Application startup complete.")

    yield  # ← application runs here

    # Shutdown
    stop_scheduler()
    await async_engine.dispose()
    logger.info("Application shutdown complete.")


# ── FastAPI app ─────────────────────────────────────────────────────────
app = FastAPI(
    title="Environmental Command Center",
    description=(
        "A production-quality API for monitoring Air Quality Index (AQI), "
        "Noise Pollution, and Sound Pollution levels."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — allow all origins for development; tighten in production. ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────
app.include_router(air_router)
app.include_router(noise_router)
app.include_router(sound_router)


# ── Health check ────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Simple health probe."""
    return {"status": "ok", "service": "Environmental Command Center"}
