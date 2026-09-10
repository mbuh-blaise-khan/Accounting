"""Tests for Session 3 authentication endpoints.

Uses the isolated SQLite test DB from conftest. Cookie-based JWT is verified via
TestClient's cookie jar.

Session 13 update — register-no-auto-login: POST /auth/register creates the
account but NO LONGER sets the session cookie. Only POST /auth/login starts a
session; the tests below pin that contract.
"""
from app.models.user import User

_PASSWORD = "supersecret123"


def _register(client, email="alice@example.com", display_name="Alice"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": _PASSWORD,
            "display_name": display_name,
            "language_preference": "en",
        },
    )


def _login(client, email="alice@example.com", password=_PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_register_success_creates_account_without_session(client):
    resp = _register(client)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"
    assert "password" not in body
    assert "hashed_password" not in body
    # register-no-auto-login: register must NOT set the httpOnly auth cookie…
    assert client.cookies.get("access_token") is None
    # …and the brand-new account must NOT be an authenticated session.
    assert client.get("/me").status_code == 401


def test_login_after_register_establishes_session(client):
    """The only way to start a session is to actively log in."""
    _register(client)
    resp = _login(client)
    assert resp.status_code == 200
    assert client.cookies.get("access_token")
    me = client.get("/me")
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"


def test_password_not_stored_in_plaintext(client, test_db_session):
    _register(client)
    user = test_db_session.query(User).filter_by(email="alice@example.com").first()
    assert user is not None
    stored = user.hashed_password
    assert stored != _PASSWORD
    assert stored.startswith("$2")  # bcrypt hash prefix


def test_duplicate_email_rejected(client):
    assert _register(client).status_code == 200
    resp = _register(client, display_name="Second")
    assert resp.status_code == 409


def test_login_success(client):
    _register(client)
    resp = _login(client)
    assert resp.status_code == 200
    assert client.cookies.get("access_token")


def test_login_wrong_password(client):
    _register(client)
    resp = _login(client, password="wrongpassword")
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = _login(client, email="nobody@example.com", password="whatever123")
    assert resp.status_code == 401


def test_me_returns_current_user_with_valid_token(client):
    _register(client)
    _login(client)
    resp = client.get("/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_me_rejects_missing_token(client):
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_rejects_invalid_token(client):
    client.cookies.set("access_token", "not.a.valid.jwt")
    assert client.get("/me").status_code == 401
