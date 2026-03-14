"""
db/session.py
─────────────
Async SQLAlchemy engine and session factory.

Provides:
    • `async_engine`  — the core async engine bound to DATABASE_URL.
    • `AsyncSessionLocal` — session factory producing `AsyncSession` instances.
    • `get_db()`       — FastAPI dependency that yields a session per-request.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# ── Engine ──────────────────────────────────────────────────────────────
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# ── Session factory ─────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async session and guarantees cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
