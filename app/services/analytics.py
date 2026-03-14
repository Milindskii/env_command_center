"""
services/analytics.py
─────────────────────
Provides aggregated pollution analytics and summary reports.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.air import AirData
from app.models.noise import NoiseData
from app.models.sound import SoundData


async def get_daily_air_summary(db: AsyncSession, city: str, days: int = 7) -> list[dict]:
    """Return average AQI, PM2.5, and PM10 per day for a city."""
    cutoff = datetime.now() - timedelta(days=days)
    stmt = (
        select(
            func.date_trunc('day', AirData.timestamp).label("day"),
            func.avg(AirData.aqi).label("avg_aqi"),
            func.avg(AirData.pm25).label("avg_pm25"),
            func.avg(AirData.pm10).label("avg_pm10"),
        )
        .where(AirData.city.ilike(f"%{city}%"))
        .where(AirData.timestamp >= cutoff)
        .group_by(func.date_trunc('day', AirData.timestamp))
        .order_by(func.date_trunc('day', AirData.timestamp).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        {
            "date": row.day.isoformat() if row.day else None,
            "avg_aqi": round(row.avg_aqi, 2) if row.avg_aqi else None,
            "avg_pm25": round(row.avg_pm25, 2) if row.avg_pm25 else None,
            "avg_pm10": round(row.avg_pm10, 2) if row.avg_pm10 else None,
        }
        for row in rows
    ]


async def get_high_pollution_alerts(db: AsyncSession, hours: int = 24) -> dict[str, list[dict]]:
    """Return cities that have had dangerous levels of pollution recently."""
    cutoff = datetime.now() - timedelta(hours=hours)

    alerts = {"air": [], "noise": [], "sound": []}

    # Air Quality Alerts (AQI > 150 is Unhealthy)
    air_stmt = (
        select(AirData.city, func.max(AirData.aqi).label("peak_aqi"))
        .where(AirData.timestamp >= cutoff)
        .group_by(AirData.city)
        .having(func.max(AirData.aqi) > 150)
    )
    for row in (await db.execute(air_stmt)).all():
        alerts["air"].append({"city": row.city, "peak_aqi": round(row.peak_aqi, 2)})

    # Noise Pollution Alerts (Noise > 85 dB is harmful)
    noise_stmt = (
        select(NoiseData.city, func.max(NoiseData.noise_db).label("peak_noise"))
        .where(NoiseData.timestamp >= cutoff)
        .group_by(NoiseData.city)
        .having(func.max(NoiseData.noise_db) > 85)
    )
    for row in (await db.execute(noise_stmt)).all():
        alerts["noise"].append({"city": row.city, "peak_noise_db": round(row.peak_noise, 2)})
        
    # Sound Pollution Alerts (Indoor > 80 dB is harmful)
    sound_stmt = (
        select(SoundData.city, func.max(SoundData.sound_db).label("peak_sound"))
        .where(SoundData.timestamp >= cutoff)
        .group_by(SoundData.city)
        .having(func.max(SoundData.sound_db) > 80)
    )
    for row in (await db.execute(sound_stmt)).all():
        alerts["sound"].append({"city": row.city, "peak_sound_db": round(row.peak_sound, 2)})

    return alerts
