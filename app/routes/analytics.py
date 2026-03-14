"""
routes/analytics.py
───────────────────
FastAPI router for aggregated pollution analytics and alerts.
"""


from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services import analytics

router = APIRouter(prefix="/analytics", tags=["Analytics & Alerts"])


@router.get("/daily-summary")
async def get_daily_summary(
    city: str = Query(..., min_length=1, description="City name"),
    days: int = Query(7, ge=1, le=30, description="Number of days to summarize"),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Get daily average pollution stats (Air) for a given city over the last N days."""
    return await analytics.get_daily_air_summary(db, city, days)


@router.get("/alerts")
async def get_alerts(
    hours: int = Query(24, ge=1, le=72, description="Lookback window in hours"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get active alerts for cities experiencing high pollution within the last N hours.
    
    Thresholds:
      - AQI > 150
      - Noise > 85 dB
      - Indoor Sound > 80 dB
    """
    return await analytics.get_high_pollution_alerts(db, hours)
