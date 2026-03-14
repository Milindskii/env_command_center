"""
routes/noise.py
───────────────
FastAPI router for noise / sound-pollution endpoints.

Endpoints
    POST /environment/noise          — insert a noise record manually
    GET  /environment/noise          — latest noise reading for a city
    GET  /environment/noise/history  — paginated noise history
"""


from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from app.db.session import get_db
from app.models.noise import NoiseData
from app.schemas.noise import NoiseDataCreate, NoiseDataRead
from app.services import noise_service

router = APIRouter(prefix="/environment/noise", tags=["Noise Pollution"])


# ── POST — manual insert ───────────────────────────────────────────────
@router.post("/", response_model=NoiseDataRead, status_code=201)
@limiter.limit("10/minute")
async def create_noise_record(
    request: Request,
    payload: NoiseDataCreate,
    db: AsyncSession = Depends(get_db),
) -> NoiseData:
    """Insert a noise-pollution record manually."""
    return await noise_service.create_noise_record_db(db, payload)


# ── GET — latest by city ───────────────────────────────────────────────
@router.get("/", response_model=NoiseDataRead)
@limiter.limit("60/minute")
async def get_latest_noise(
    request: Request,
    city: str = Query(..., min_length=1, description="City name"),
    db: AsyncSession = Depends(get_db),
) -> NoiseData:
    """Return the most recent noise record for the given city."""
    record = await noise_service.get_latest_noise_db(db, city)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No noise data found for city '{city}'")
    return record


# ── GET — paginated history ────────────────────────────────────────────
@router.get("/history", response_model=list[NoiseDataRead])
@limiter.limit("30/minute")
async def get_noise_history(
    request: Request,
    city: str = Query(..., min_length=1, description="City name"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    db: AsyncSession = Depends(get_db),
) -> list[NoiseData]:
    """Return paginated noise history for the given city."""
    return await noise_service.get_noise_history_db(db, city, limit, offset)
