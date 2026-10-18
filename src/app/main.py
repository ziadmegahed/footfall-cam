from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes.api import router
from db.db_counter import init_db

BASE = Path(__file__).resolve().parents[2]

init_db()

app = FastAPI(
    title="Footfall Analytics API",
    version="0.1.0",
    description="Retail visitor analytics platform",
)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
