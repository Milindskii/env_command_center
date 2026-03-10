from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base

class AirData(Base):
    __tablename__ = "air_data"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    aqi = Column(Integer)
    pm25 = Column(Integer)
    pm10 = Column(Integer)
    status = Column(String)
