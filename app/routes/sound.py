"""
routes/sound.py
───────────────
FastAPI router for sound-pollution endpoints.

Endpoints
    POST /environment/sound          — insert a sound record manually
    GET  /environment/sound          — latest sound reading for a city
    GET  /environment/sound/history  — paginated sound history
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.sound import SoundData
from app.schemas.sound import SoundDataCreate, SoundDataRead

router = APIRouter(prefix="/environment/sound", tags=["Sound Pollution (Indoor)"])


# ── POST — manual insert ───────────────────────────────────────────────
@router.post("/", response_model=SoundDataRead, status_code=201)
async def create_sound_record(
    payload: SoundDataCreate,
    db: AsyncSession = Depends(get_db),
) -> SoundData:
    """Insert a sound-pollution record manually."""
    record = SoundData(**payload.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


# ── GET — latest by city ───────────────────────────────────────────────
@router.get("/", response_model=SoundDataRead)
async def get_latest_sound(
    city: str = Query(..., min_length=1, description="City name"),
    db: AsyncSession = Depends(get_db),
) -> SoundData:
    """Return the most recent sound record for the given city."""
    stmt = (
        select(SoundData)
        .where(SoundData.city.ilike(f"%{city}%"))
        .order_by(SoundData.timestamp.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail=f"No sound data found for city '{city}'")
    return record


# ── GET — paginated history ────────────────────────────────────────────
@router.get("/history", response_model=list[SoundDataRead])
async def get_sound_history(
    city: str = Query(..., min_length=1, description="City name"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    db: AsyncSession = Depends(get_db),
) -> list[SoundData]:
    """Return paginated sound history for the given city."""
    stmt = (
        select(SoundData)
        .where(SoundData.city.ilike(f"%{city}%"))
        .order_by(SoundData.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
