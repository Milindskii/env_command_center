"""
services/updater.py
───────────────────
Orchestrates periodic environment-data collection.

Called by the scheduler every 10 minutes to:
1. Fetch AQI for every configured city.
2. Generate simulated noise readings for every configured city.
3. Persist new rows in PostgreSQL.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sqlalchemy import delete

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.air import AirData
from app.models.noise import NoiseData
from app.models.sound import SoundData
from app.services.aqi_client import fetch_aqi
from app.services.noise_client import fetch_noise
from app.services.sound_client import fetch_sound

logger = logging.getLogger(__name__)


async def update_all_environmental_data() -> None:
    """Fetch and persist AQI + noise data for every monitored city."""
    cities = settings.city_list
    logger.info("Updater running for cities: %s", cities)

    async with AsyncSessionLocal() as session:
        for city in cities:
            # ── Air quality ─────────────────────────────────────────
            aqi_data = await fetch_aqi(city)
            if aqi_data:
                session.add(
                    AirData(
                        city=aqi_data["city"],
                        aqi=aqi_data["aqi"],
                        pm25=aqi_data.get("pm25"),
                        pm10=aqi_data.get("pm10"),
                        status=aqi_data["status"],
                    )
                )
                logger.info("AQI stored for %s: %s", city, aqi_data["aqi"])
            else:
                logger.warning("Skipped AQI for %s — upstream unavailable", city)

            # ── Noise pollution (Outdoor) ───────────────────────────
            noise_data = await fetch_noise(city)
            session.add(
                NoiseData(
                    city=noise_data["city"],
                    noise_db=noise_data["noise_db"],
                    noise_level=noise_data["noise_level"],
                    status=noise_data["status"],
                )
            )
            logger.info("Noise stored for %s: %s dB", city, noise_data["noise_db"])

            # ── Sound pollution (Indoor) ────────────────────────────
            sound_data = await fetch_sound(city)
            session.add(
                SoundData(
                    city=sound_data["city"],
                    sound_db=sound_data["sound_db"],
                    environment=sound_data["environment"],
                    status=sound_data["status"],
                )
            )
            logger.info("Sound stored for %s: %s dB", city, sound_data["sound_db"])

        await session.commit()
        logger.info("Updater cycle complete — committed all records.")


async def prune_old_data(days: int = 30) -> None:
    """Delete raw environment records older than the specified number of days."""
    cutoff = datetime.now() - timedelta(days=days)
    logger.info("Pruning environment data older than %s days (cutoff: %s)", days, cutoff)

    async with AsyncSessionLocal() as session:
        # AirData
        stmt_air = delete(AirData).where(AirData.timestamp < cutoff)
        result_air = await session.execute(stmt_air)

        # NoiseData
        stmt_noise = delete(NoiseData).where(NoiseData.timestamp < cutoff)
        result_noise = await session.execute(stmt_noise)

        # SoundData
        stmt_sound = delete(SoundData).where(SoundData.timestamp < cutoff)
        result_sound = await session.execute(stmt_sound)

        await session.commit()
        logger.info(
            "Pruning complete. Deleted Air: %d, Noise: %d, Sound: %d",
            result_air.rowcount,
            result_noise.rowcount,
            result_sound.rowcount,
        )
