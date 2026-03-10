from fastapi import FastAPI
from app.routes.air import router as air_router
from app.db.session import engine
from app.db.base import Base
from app.models.air import AirData


app = FastAPI(title="Environmental Command Center")
Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(air_router)
