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

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from app.db.session import get_db
from app.models.air import AirData
from app.schemas.air import AirDataCreate, AirDataRead
from app.services import air_service

router = APIRouter(prefix="/environment/air", tags=["Air Quality"])


# ── POST — manual insert ───────────────────────────────────────────────
@router.post("/", response_model=AirDataRead, status_code=201)
@limiter.limit("10/minute")
async def create_air_record(
    request: Request,
    payload: AirDataCreate,
    db: AsyncSession = Depends(get_db),
) -> AirData:
    """Insert an air-quality record manually."""
    return await air_service.create_air_record_db(db, payload)


# ── GET — latest by city ───────────────────────────────────────────────
@router.get("/", response_model=AirDataRead)
@limiter.limit("60/minute")
async def get_latest_air(
    request: Request,
    city: str = Query(..., min_length=1, description="City name"),
    db: AsyncSession = Depends(get_db),
) -> AirData:
    """Return the most recent AQI record for the given city."""
    record = await air_service.get_latest_air_db(db, city)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No air data found for city '{city}'")
    return record


# ── GET — paginated history ────────────────────────────────────────────
@router.get("/history", response_model=list[AirDataRead])
@limiter.limit("30/minute")
async def get_air_history(
    request: Request,
    city: str = Query(..., min_length=1, description="City name"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    db: AsyncSession = Depends(get_db),
) -> list[AirData]:
    """Return paginated AQI history for the given city."""
    return await air_service.get_air_history_db(db, city, limit, offset)