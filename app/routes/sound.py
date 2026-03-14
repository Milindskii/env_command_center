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

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from app.db.session import get_db
from app.models.sound import SoundData
from app.schemas.sound import SoundDataCreate, SoundDataRead
from app.services import sound_service

router = APIRouter(prefix="/environment/sound", tags=["Sound Pollution (Indoor)"])


# ── POST — manual insert ───────────────────────────────────────────────
@router.post("/", response_model=SoundDataRead, status_code=201)
@limiter.limit("10/minute")
async def create_sound_record(
    request: Request,
    payload: SoundDataCreate,
    db: AsyncSession = Depends(get_db),
) -> SoundData:
    """Insert a sound-pollution record manually."""
    return await sound_service.create_sound_record_db(db, payload)


# ── GET — latest by city ───────────────────────────────────────────────
@router.get("/", response_model=SoundDataRead)
@limiter.limit("60/minute")
async def get_latest_sound(
    request: Request,
    city: str = Query(..., min_length=1, description="City name"),
    db: AsyncSession = Depends(get_db),
) -> SoundData:
    """Return the most recent sound record for the given city."""
    record = await sound_service.get_latest_sound_db(db, city)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No sound data found for city '{city}'")
    return record


# ── GET — paginated history ────────────────────────────────────────────
@router.get("/history", response_model=list[SoundDataRead])
@limiter.limit("30/minute")
async def get_sound_history(
    request: Request,
    city: str = Query(..., min_length=1, description="City name"),
    limit: int = Query(20, ge=1, le=100, description="Records per page"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    db: AsyncSession = Depends(get_db),
) -> list[SoundData]:
    """Return paginated sound history for the given city."""
    return await sound_service.get_sound_history_db(db, city, limit, offset)
