"""Tests for Session 3 authentication endpoints.

Uses the isolated SQLite test DB from conftest. Cookie-based JWT is verified via
TestClient's cookie jar.
"""
from app.models.user import User


def _register(client, **overrides):
    data = {
        "email": "alice@example.com",
        "password": "supersecret123",
        "display_name": "Alice",
        "language_preference": "en",
        **overrides,
    }
    return client.post("/auth/register", json=data)


def test_register_success_sets_cookie_and_hashes_password(client):
    resp = _register(client)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"
    assert "password" not in body
    assert "hashed_password" not in body
    # JWT is delivered as an httpOnly cookie.
    assert client.cookies.get("access_token")


def test_password_not_stored_in_plaintext(client, test_db_session):
    _register(client)
    user = test_db_session.query(User).filter_by(email="alice@example.com").first()
    assert user is not None
    stored = user.hashed_password
    assert stored != "supersecret123"
    assert stored.startswith("$2")  # bcrypt hash prefix


def test_duplicate_email_rejected(client):
    assert _register(client).status_code == 200
    resp = _register(client, display_name="Second")
    assert resp.status_code == 409


def test_login_success(client):
    _register(client)
    client.cookies.clear()
    resp = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "supersecret123"},
    )
    assert resp.status_code == 200
    assert client.cookies.get("access_token")


def test_login_wrong_password(client):
    _register(client)
    resp = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )
    assert resp.status_code == 401


def test_me_returns_current_user_with_valid_token(client):
    _register(client)
    resp = client.get("/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_me_rejects_missing_token(client):
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_rejects_invalid_token(client):
    client.cookies.set("access_token", "not.a.valid.jwt")
    resp = client.get("/me")
    assert resp.status_code == 401
