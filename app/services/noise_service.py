"""
services/noise_service.py
─────────────────────────
Business logic and database operations for Noise Pollution data.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.noise import NoiseData
from app.schemas.noise import NoiseDataCreate


async def create_noise_record_db(db: AsyncSession, payload: NoiseDataCreate) -> NoiseData:
    """Insert a noise-pollution record into the database."""
    record = NoiseData(**payload.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_latest_noise_db(db: AsyncSession, city: str) -> NoiseData | None:
    """Return the most recent noise-pollution record for the given city."""
    stmt = (
        select(NoiseData)
        .where(NoiseData.city.ilike(f"%{city}%"))
        .order_by(NoiseData.timestamp.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_noise_history_db(db: AsyncSession, city: str, limit: int, offset: int) -> list[NoiseData]:
    """Return paginated noise-pollution history for the given city."""
    stmt = (
        select(NoiseData)
        .where(NoiseData.city.ilike(f"%{city}%"))
        .order_by(NoiseData.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
