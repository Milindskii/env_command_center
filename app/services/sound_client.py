"""
services/sound_client.py
────────────────────────
Indoor / occupational sound data provider.

This module simulates realistic sound readings for indoor environments
like factories, offices, and homes, allowing us to track "sound pollution"
separately from outdoor "noise pollution".
"""

from __future__ import annotations

import random
from typing import Any

# ── Sound profile definitions ──────────────────────────────────────────
_SOUND_PROFILES: list[dict[str, Any]] = [
    {"range": (30, 45), "env": "Library / Quiet Room", "weight": 0.20},
    {"range": (45, 60), "env": "Normal Office", "weight": 0.40},
    {"range": (60, 75), "env": "Busy Restaurant", "weight": 0.25},
    {"range": (75, 90), "env": "Factory Floor", "weight": 0.10},
    {"range": (90, 105), "env": "Heavy Machinery", "weight": 0.05},
]

def _sound_status(db: float) -> str:
    """Derive a status label from an indoor decibel reading."""
    if db < 50:
        return "Excellent"
    if db < 65:
        return "Normal"
    if db < 80:
        return "Distracting"
    if db < 90:
        return "Warning: Ear Protection Advised"
    return "Hazardous: Damage Possible"


async def fetch_sound(city: str) -> dict[str, Any]:
    """Return a simulated indoor sound reading for *city*."""
    weights = [p["weight"] for p in _SOUND_PROFILES]
    profile = random.choices(_SOUND_PROFILES, weights=weights, k=1)[0]
    low, high = profile["range"]
    sound_db = round(random.uniform(low, high), 1)

    return {
        "city": city,
        "sound_db": sound_db,
        "environment": profile["env"],
        "status": _sound_status(sound_db),
    }
