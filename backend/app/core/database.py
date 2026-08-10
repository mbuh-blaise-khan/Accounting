"""SQLAlchemy database setup: engine, session factory, declarative base.

The engine is created lazily (SQLAlchemy does not connect until first use), so
importing this module is safe even when the database is down. Actual reachability
is probed by :func:`check_db_connection`.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models (Session 3+)."""


def get_db():
    """FastAPI dependency yielding a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Probe the database with a real connection + SELECT 1.

    Returns True if reachable, False otherwise. This is the source of truth for
    the /health endpoint's "db" field.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 - any failure means "not reachable"
        return False
