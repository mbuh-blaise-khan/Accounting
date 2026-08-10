"""Tests for the /health endpoint (Session 2)."""
from fastapi.testclient import TestClient

from app.core import database
from app.main import app

client = TestClient(app)


def test_health_returns_ok_when_db_up(monkeypatch):
    monkeypatch.setattr(database, "check_db_connection", lambda: True)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": True}


def test_health_reports_db_down(monkeypatch):
    monkeypatch.setattr(database, "check_db_connection", lambda: False)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": False}


def test_health_against_live_db():
    """Integration check: if the real DB is reachable, /health must say db:true."""
    if not database.check_db_connection():
        # Skip rather than fail on machines without a running database.
        import pytest

        pytest.skip("Live database not reachable")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["db"] is True
