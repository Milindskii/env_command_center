from pydantic import BaseModel
from datetime import datetime
from typing import List

class AirDataCreate(BaseModel):
    city: str
    aqi: int
    pm25: int
    pm10: int
    status: str


class AirQualityResponse(BaseModel):
    city: str
    timestamp: datetime
    aqi: int
    pm25: int
    pm10: int
    status: str

    class Config:
        from_attributes = True


class AirQualitySeriesResponse(BaseModel):
    city: str
    records: List[AirQualityResponse]
    