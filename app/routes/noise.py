"""
routes/noise.py
───────────────
FastAPI router for noise / sound-pollution endpoints.

Endpoints
    POST /environment/noise          — insert a noise record manually
    GET  /environment/noise          — latest noise reading for a city
    GET  /environment/noise/history  — paginated noise history
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.noise import NoiseData
from app.schemas.noise import NoiseDataCreate, NoiseDataRead

router = APIRouter(prefix="/environment/noise", tags=["Noise Pollution"])


# ── POST — manual insert ───────────────────────────────────────────────
@router.post("/", response_model=NoiseDataRead, status_code=201)
async def create_noise_record(
    payload: NoiseDataCreate,
    db: AsyncSession = Depends(get_db),
) -> NoiseData:
    """Insert a noise-pollution record manually."""
    record = NoiseData(**payload.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


# ── GET — latest by city ───────────────────────────────────────────────
@router.get("/", response_model=NoiseDataRead)
async def get_latest_noise(
    city: str = Query(..., min_length=1, description="City name"),
    db: AsyncSession = Depends(get_db),
) -> NoiseData:
    """Return the most recent noise record for the given city."""
    stmt = (
        select(NoiseData)
        .where(NoiseData.city.ilike(f"%{city}%"))
        .order_by(NoiseData.timestamp.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail=f"No noise data found for city '{city}'")
    return record


# ── GET — paginated history ────────────────────────────────────────────
@router.get("/history", response_model=list[NoiseDataRead])
async def get_noise_history(
    city: str = Query(..., min_length=1, description="City name"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    db: AsyncSession = Depends(get_db),
) -> list[NoiseData]:
    """Return paginated noise history for the given city."""
    stmt = (
        select(NoiseData)
        .where(NoiseData.city.ilike(f"%{city}%"))
        .order_by(NoiseData.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
