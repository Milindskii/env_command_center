"""
schemas/noise.py
────────────────
Pydantic v2 schemas for noise / sound-pollution request/response validation.

Schemas
    NoiseDataCreate  — payload accepted by POST /environment/noise
    NoiseDataRead    — shape returned by GET endpoints
"""


from datetime import datetime

from pydantic import BaseModel, Field


class NoiseDataCreate(BaseModel):
    """Schema for manually inserting a noise-pollution record."""

    city: str = Field(..., min_length=1, max_length=120, examples=["mumbai"])
    noise_db: float = Field(..., ge=0, examples=[72.5])
    noise_level: str = Field("unknown", max_length=50, examples=["Urban Traffic"])
    status: str = Field("unknown", max_length=50, examples=["Moderate"])


class NoiseDataRead(BaseModel):
    """Schema returned to the client for noise-pollution records."""

    id: int
    city: str
    timestamp: datetime
    noise_db: float
    noise_level: str
    status: str

    model_config = {"from_attributes": True}
