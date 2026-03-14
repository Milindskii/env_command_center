"""
models/sound.py
───────────────
SQLAlchemy ORM model for indoor/occupational sound-level readings.

Maps to the ``sound_data`` table which stores decibel-level snapshots
specifically for indoor or localized environments.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SoundData(Base):
    """Persisted sound-level measurement for a given location or city."""

    __tablename__ = "sound_data"
    __table_args__ = (
        Index("ix_sound_data_city_timestamp", "city", "timestamp"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    sound_db: Mapped[float] = mapped_column(Float, nullable=False)
    environment: Mapped[str] = mapped_column(String(100), nullable=False, default="Indoor")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")

    def __repr__(self) -> str:
        return (
            f"<SoundData city={self.city!r} sound_db={self.sound_db} "
            f"environment={self.environment!r}>"
        )
