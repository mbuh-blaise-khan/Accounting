"""Tests for Session 4 organization/workspace + framework-selection endpoints."""
from app.models.enums import MembershipRole
from app.models.organization import OrganizationMember


def _register(client, email="alice@example.com"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "display_name": "Alice",
            "language_preference": "en",
        },
    )


def _create_org(client, **overrides):
    data = {"name": "Acme", "framework": "OHADA", "currency": "XAF", **overrides}
    return client.post("/organizations", json=data)


def test_create_org_attaches_creator_as_owner(client, test_db_session):
    _register(client)
    resp = _create_org(client)
    assert resp.status_code == 201
    org = resp.json()
    assert org["name"] == "Acme"
    assert org["framework"] == "OHADA"
    assert org["currency"] == "XAF"
    assert org["is_demo"] is False

    membership = (
        test_db_session.query(OrganizationMember)
        .filter(OrganizationMember.org_id == org["id"])
        .first()
    )
    assert membership is not None
    assert membership.user_id == org["owner_user_id"]
    assert membership.role == MembershipRole.owner


def test_create_org_defaults_currency_when_omitted(client):
    _register(client)
    payload = {"name": "Acme", "framework": "IFRS"}
    resp = client.post("/organizations", json=payload)
    assert resp.status_code == 201
    assert resp.json()["currency"] == "XAF"


def test_list_organizations_only_from_my_memberships(client):
    _register(client)
    org = _create_org(client).json()
    resp = client.get("/organizations")
    assert resp.status_code == 200
    ids = [o["id"] for o in resp.json()]
    assert org["id"] in ids


def test_cannot_access_another_users_organization(client):
    alice_org = None
    _register(client, "alice@example.com")
    alice_org = _create_org(client).json()

    # Bob registers (same TestClient, cookies replaced by login-less register).
    _register(client, "bob@example.com")
    resp = client.get(f"/organizations/{alice_org['id']}")
    assert resp.status_code == 404  # not 403: do not reveal existence

    # Bob's list does NOT include Alice's org.
    resp = client.get("/organizations")
    assert resp.status_code == 200
    ids = [o["id"] for o in resp.json()]
    assert alice_org["id"] not in ids


def test_create_demo_workspace_flag(client):
    _register(client)
    resp = _create_org(client, name="Sample Demo Business", is_demo=True)
    assert resp.status_code == 201
    assert resp.json()["is_demo"] is True


def test_frameworks_listed_with_descriptions_and_versions(client):
    _register(client)
    resp = client.get("/frameworks")
    assert resp.status_code == 200
    data = resp.json()
    codes = {fw["code"] for fw in data}
    assert codes == {"OHADA", "IFRS"}
    for fw in data:
        assert fw["description_en"]
        assert fw["description_fr"]
        assert len(fw["versions"]) >= 1
        assert any(v["is_current"] for v in fw["versions"])


def test_unauthenticated_org_access_rejected(client):
    resp = client.get("/organizations")
    assert resp.status_code == 401