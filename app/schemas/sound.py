"""
schemas/sound.py
────────────────
Pydantic v2 schemas for sound-level request/response validation.

Schemas
    SoundDataCreate  — payload accepted by POST /environment/sound
    SoundDataRead    — shape returned by GET endpoints
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SoundDataCreate(BaseModel):
    """Schema for manually inserting a sound-level record."""

    city: str = Field(..., min_length=1, max_length=120, examples=["mumbai"])
    sound_db: float = Field(..., ge=0, examples=[55.0])
    environment: str = Field("Indoor", max_length=100, examples=["Office"])
    status: str = Field("unknown", max_length=50, examples=["Normal"])


class SoundDataRead(BaseModel):
    """Schema returned to the client for sound-level records."""

    id: int
    city: str
    timestamp: datetime
    sound_db: float
    environment: str
    status: str

    model_config = {"from_attributes": True}
