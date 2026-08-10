"""Health check endpoint. Exercises a real database round-trip."""
from fastapi import APIRouter

from app.core import database

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Return service and database status."""
    return {"status": "ok", "db": database.check_db_connection()}
