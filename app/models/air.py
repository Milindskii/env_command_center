"""
models/air.py
─────────────
SQLAlchemy ORM model for air-quality readings.

Maps to the ``air_data`` table which stores AQI snapshots fetched
from the WAQI API or inserted manually.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AirData(Base):
    """Persisted air-quality measurement for a given city."""

    __tablename__ = "air_data"
    __table_args__ = (
        Index("ix_air_data_city_timestamp", "city", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    aqi: Mapped[float] = mapped_column(Float, nullable=False)
    pm25: Mapped[float | None] = mapped_column(Float, nullable=True)
    pm10: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")

    def __repr__(self) -> str:
        return f"<AirData city={self.city!r} aqi={self.aqi} status={self.status!r}>"
