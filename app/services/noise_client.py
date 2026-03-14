"""
services/noise_client.py
────────────────────────
Noise / sound-pollution data provider.

Since no reliable *free* real-time noise API exists at the time of writing,
this module **simulates** realistic noise readings using weighted random
distributions that vary by time of day.

If a real API becomes available in the future, swap the implementation of
``fetch_noise()`` — the interface remains unchanged.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any


# ── Noise profile definitions ──────────────────────────────────────────
_NOISE_PROFILES: list[dict[str, Any]] = [
    {"range": (30, 50), "level": "Quiet Area", "weight_day": 0.15, "weight_night": 0.55},
    {"range": (50, 65), "level": "Moderate", "weight_day": 0.25, "weight_night": 0.30},
    {"range": (65, 80), "level": "Urban Traffic", "weight_day": 0.35, "weight_night": 0.10},
    {"range": (80, 95), "level": "Heavy Noise Pollution", "weight_day": 0.18, "weight_night": 0.04},
    {"range": (95, 110), "level": "Dangerously Loud", "weight_day": 0.07, "weight_night": 0.01},
]


def _noise_status(db: float) -> str:
    """Derive a status label from a decibel reading."""
    if db < 55:
        return "Good"
    if db < 70:
        return "Moderate"
    if db < 85:
        return "Unhealthy"
    if db < 100:
        return "Very Unhealthy"
    return "Hazardous"


async def fetch_noise(city: str) -> dict[str, Any]:
    """Return a simulated noise reading for *city*.

    During daytime (06:00–22:00 UTC) the distribution skews toward higher
    decibels; at night it skews toward quieter readings.
    """
    hour = datetime.now(tz=timezone.utc).hour
    is_daytime = 6 <= hour < 22

    weights = [
        p["weight_day"] if is_daytime else p["weight_night"]
        for p in _NOISE_PROFILES
    ]

    profile = random.choices(_NOISE_PROFILES, weights=weights, k=1)[0]
    low, high = profile["range"]
    noise_db = round(random.uniform(low, high), 1)

    return {
        "city": city,
        "noise_db": noise_db,
        "noise_level": profile["level"],
        "status": _noise_status(noise_db),
    }
