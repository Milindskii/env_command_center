"""
routes/air.py
─────────────
FastAPI router for air-quality endpoints.

Endpoints
    POST /environment/air          — insert an air-quality record manually
    GET  /environment/air          — latest AQI for a city
    GET  /environment/air/history  — paginated AQI history
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.air import AirData
from app.schemas.air import AirDataCreate, AirDataRead

router = APIRouter(prefix="/environment/air", tags=["Air Quality"])


# ── POST — manual insert ───────────────────────────────────────────────
@router.post("/", response_model=AirDataRead, status_code=201)
async def create_air_record(
    payload: AirDataCreate,
    db: AsyncSession = Depends(get_db),
) -> AirData:
    """Insert an air-quality record manually."""
    record = AirData(**payload.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


# ── GET — latest by city ───────────────────────────────────────────────
@router.get("/", response_model=AirDataRead)
async def get_latest_air(
    city: str = Query(..., min_length=1, description="City name"),
    db: AsyncSession = Depends(get_db),
) -> AirData:
    """Return the most recent AQI record for the given city."""
    stmt = (
        select(AirData)
        .where(AirData.city.ilike(f"%{city}%"))
        .order_by(AirData.timestamp.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail=f"No air data found for city '{city}'")
    return record


# ── GET — paginated history ────────────────────────────────────────────
@router.get("/history", response_model=list[AirDataRead])
async def get_air_history(
    city: str = Query(..., min_length=1, description="City name"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    db: AsyncSession = Depends(get_db),
) -> list[AirData]:
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