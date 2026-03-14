"""
schemas/air.py
──────────────
Pydantic v2 schemas for air-quality request/response validation.

Schemas
    AirDataCreate  — payload accepted by POST /environment/air
    AirDataRead    — shape returned by GET endpoints
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AirDataCreate(BaseModel):
    """Schema for manually inserting an air-quality record."""

    city: str = Field(..., min_length=1, max_length=120, examples=["delhi"])
    aqi: float = Field(..., ge=0, examples=[152.0])
    pm25: float | None = Field(None, ge=0, examples=[75.3])
    pm10: float | None = Field(None, ge=0, examples=[120.0])
    status: str = Field("unknown", max_length=50, examples=["Unhealthy"])


class AirDataRead(BaseModel):
    """Schema returned to the client for air-quality records."""

    id: int
    city: str
    timestamp: datetime
    aqi: float
    pm25: float | None
    pm10: float | None
    status: str

    model_config = {"from_attributes": True}