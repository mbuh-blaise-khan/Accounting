"""Pytest fixtures for the backend.

Tests run against an isolated in-memory SQLite database (not the dev Postgres)
so auth/accounting tests never mutate real data. The app's `get_db` dependency
is overridden to hand out sessions bound to the test engine.
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# backend/app/tests/conftest.py -> parents[0]=tests, [1]=app, [2]=backend
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.services.framework_service import ensure_default_frameworks  # noqa: E402

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _test_schema():
    Base.metadata.create_all(bind=engine)
    # Seed the framework registry once (OHADA + IFRS) for tests that read it.
    session = TestingSessionLocal()
    try:
        ensure_default_frameworks(session)
    finally:
        session.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """TestClient whose /auth, /me etc. hit the SQLite test DB."""

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _clean_users_between_tests():
    """Isolate tests: wipe data after each test.

    Without this, a user created in one test would persist (same in-memory DB
    connection via StaticPool) and break duplicate-email/login expectations.
    """
    yield
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM organization_members"))
        conn.execute(text("DELETE FROM organizations"))
        conn.execute(text("DELETE FROM users"))


@pytest.fixture()
def test_db_session():
    """A session bound to the same test engine (for direct DB assertions)."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
