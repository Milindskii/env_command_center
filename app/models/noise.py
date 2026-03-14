"""
models/noise.py
───────────────
SQLAlchemy ORM model for noise / sound-pollution readings.

Maps to the ``noise_data`` table which stores decibel-level snapshots
fetched from an external API or generated via simulation.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NoiseData(Base):
    """Persisted noise-pollution measurement for a given city."""

    __tablename__ = "noise_data"
    __table_args__ = (
        Index("ix_noise_data_city_timestamp", "city", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    noise_db: Mapped[float] = mapped_column(Float, nullable=False)
    noise_level: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")

    def __repr__(self) -> str:
        return (
            f"<NoiseData city={self.city!r} noise_db={self.noise_db} "
            f"level={self.noise_level!r}>"
        )
