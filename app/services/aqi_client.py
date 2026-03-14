"""
services/aqi_client.py
──────────────────────
Async client for the World Air Quality Index (WAQI) public API.

Endpoint used:
    https://api.waqi.info/feed/{city}/?token={AQI_API_KEY}

The response JSON root contains:
    • status  — "ok" | "error"
    • data.aqi
    • data.iaqi.pm25.v
    • data.iaqi.pm10.v
    • data.city.name
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── AQI → human-readable status mapping ────────────────────────────────
_AQI_BREAKPOINTS: list[tuple[int, str]] = [
    (50, "Good"),
    (100, "Moderate"),
    (150, "Unhealthy for Sensitive Groups"),
    (200, "Unhealthy"),
    (300, "Very Unhealthy"),
]


def _aqi_status(aqi: float) -> str:
    """Return a human-readable status string for a numeric AQI value."""
    for threshold, label in _AQI_BREAKPOINTS:
        if aqi <= threshold:
            return label
    return "Hazardous"


async def fetch_aqi(city: str) -> dict[str, Any] | None:
    """Fetch the latest AQI reading for *city* from WAQI.

    Returns a dict with keys ``city``, ``aqi``, ``pm25``, ``pm10``, and
    ``status``, or ``None`` when the upstream call fails / returns an error.
    """
    url = f"https://api.waqi.info/feed/{city}/?token={settings.AQI_API_KEY}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()

        if payload.get("status") != "ok":
            logger.warning("WAQI API returned non-ok status for %s: %s", city, payload)
            return None

        data = payload["data"]
        aqi_value = float(data["aqi"])
        iaqi = data.get("iaqi", {})

        return {
            "city": data.get("city", {}).get("name", city),
            "aqi": aqi_value,
            "pm25": iaqi.get("pm25", {}).get("v"),
            "pm10": iaqi.get("pm10", {}).get("v"),
            "status": _aqi_status(aqi_value),
        }

    except httpx.HTTPStatusError as exc:
        logger.error("WAQI HTTP error for %s: %s", city, exc)
    except httpx.RequestError as exc:
        logger.error("WAQI request error for %s: %s", city, exc)
    except (KeyError, ValueError, TypeError) as exc:
        logger.error("Unexpected WAQI response structure for %s: %s", city, exc)

    return None
