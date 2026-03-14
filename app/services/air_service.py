"""
services/air_service.py
───────────────────────
Business logic and database operations for Air Quality data.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.air import AirData
from app.schemas.air import AirDataCreate


async def create_air_record_db(db: AsyncSession, payload: AirDataCreate) -> AirData:
    """Insert an air-quality record into the database."""
    record = AirData(**payload.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_latest_air_db(db: AsyncSession, city: str) -> AirData | None:
    """Return the most recent AQI record for the given city."""
    stmt = (
        select(AirData)
        .where(AirData.city.ilike(f"%{city}%"))
        .order_by(AirData.timestamp.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_air_history_db(db: AsyncSession, city: str, limit: int, offset: int) -> list[AirData]:
    """Return paginated AQI history for the given city."""
    stmt = (
        select(AirData)
        .where(AirData.city.ilike(f"%{city}%"))
        .order_by(AirData.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
