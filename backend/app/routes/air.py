"""
Air Quality Routes
------------------
Handles CRUD operations for air quality data.

Prefix: /environment/air
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Database session dependency
from app.db.session import get_db

# ORM model (represents air_data table)
from app.models.air import AirData

# Pydantic schemas (request + response validation)
from app.schemas.air import (
    AirQualityResponse,
    AirQualitySeriesResponse,
    AirDataCreate,
)

# Router configuration
router = APIRouter(
    prefix="/environment/air",
    tags=["Air Quality"]
)


# ------------------------------------------------------------
# CREATE
# ------------------------------------------------------------
@router.post(
    "",
    response_model=AirQualityResponse,
    summary="Create new air quality record"
)
def create_air_data(
    data: AirDataCreate,
    db: Session = Depends(get_db)
):
    """
    Inserts a new air quality record into the database.

    - Validates input using AirDataCreate schema
    - Creates ORM object
    - Commits transaction
    - Returns created record
    """

    # Convert Pydantic model → ORM model
    new_record = AirData(**data.model_dump())

    db.add(new_record)       # Stage insert
    db.commit()              # Write to DB
    db.refresh(new_record)   # Reload to get generated fields (id, timestamp)

    return new_record


# ------------------------------------------------------------
# READ (Latest Record by City)
# ------------------------------------------------------------
@router.get(
    "",
    response_model=AirQualityResponse,
    summary="Get latest air quality record for a city"
)
def get_latest_air(
    city: str,
    db: Session = Depends(get_db)
):
    """
    Returns the most recent air quality record for a given city.

    - Filters by city
    - Orders by timestamp descending
    - Returns first (latest) result
    """

    record = (
        db.query(AirData)
        .filter(AirData.city == city)
        .order_by(AirData.timestamp.desc())
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    return record


# ------------------------------------------------------------
# READ (History with Pagination)
# ------------------------------------------------------------
@router.get(
    "/history",
    response_model=AirQualitySeriesResponse,
    summary="Get air quality history for a city"
)
def get_air_quality_history(
    city: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Returns paginated air quality history.

    Parameters:
    - city: required city name
    - limit: number of records to return
    - offset: starting position (for pagination)

    Query flow:
    - Filter by city
    - Order by latest first
    - Apply offset
    - Apply limit
    """

    records = (
        db.query(AirData)
        .filter(AirData.city == city)
        .order_by(AirData.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return AirQualitySeriesResponse(
        city=city,
        records=records
    )