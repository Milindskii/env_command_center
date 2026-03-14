"""
services/sound_service.py
─────────────────────────
Business logic and database operations for Sound Level data (Indoor/Occupational).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sound import SoundData
from app.schemas.sound import SoundDataCreate


async def create_sound_record_db(db: AsyncSession, payload: SoundDataCreate) -> SoundData:
    """Insert a sound-level record into the database."""
    record = SoundData(**payload.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_latest_sound_db(db: AsyncSession, city: str) -> SoundData | None:
    """Return the most recent sound-level record for the given city."""
    stmt = (
        select(SoundData)
        .where(SoundData.city.ilike(f"%{city}%"))
        .order_by(SoundData.timestamp.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_sound_history_db(db: AsyncSession, city: str, limit: int, offset: int) -> list[SoundData]:
    """Return paginated sound-level history for the given city."""
    stmt = (
        select(SoundData)
        .where(SoundData.city.ilike(f"%{city}%"))
        .order_by(SoundData.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
