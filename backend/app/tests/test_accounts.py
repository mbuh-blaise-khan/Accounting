"""Tests for Session 5 chart of accounts: seed, CRUD, validation, authorization."""
from app.services.account_service import (
    ILLUSTRATIVE_CHART,
    has_posted_transactions,
    seed_illustrative_chart,
)


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


def _create_org(client, name="Acme", framework="OHADA", is_demo=False):
    return client.post(
        "/organizations",
        json={"name": name, "framework": framework, "currency": "XAF", "is_demo": is_demo},
    )


def _post_account(client, org_id, framework="OHADA", code="9999", **overrides):
    data = {
        "organization_id": org_id,
        "framework": framework,
        "code": code,
        "name_en": "Custom account",
        "name_fr": "Compte personnalisé",
        "account_class": "expense",
        "normal_balance": "debit",
        **overrides,
    }
    return client.post("/accounts", json=data)


def test_seed_illustrative_chart_runs_cleanly(client, test_db_session):
    _register(client)
    org = _create_org(client, is_demo=False).json()

    created = seed_illustrative_chart(test_db_session, org["id"])
    # Idempotent: a second run adds nothing.
    again = seed_illustrative_chart(test_db_session, org["id"])

    assert len(created) == len(ILLUSTRATIVE_CHART)
    assert again == []
    for acc in test_db_session.query(type(created[0])).all():
        assert acc.is_system_default is True
        assert acc.active is True
        assert acc.normal_balance in ("debit", "credit")
    # Every class + normal balance pair is internally consistent in the seed.
    for item in ILLUSTRATIVE_CHART:
        assert item["normal_balance"] in ("debit", "credit")


def test_demo_org_auto_seeds_illustrative_chart(client):
    """Creating a demo workspace seeds its chart immediately (Session 5 hook)."""
    _register(client)
    org = _create_org(client, is_demo=True).json()

    resp = client.get(f"/accounts?organization_id={org['id']}")
    assert resp.status_code == 200
    accounts = resp.json()
    assert len(accounts) == len(ILLUSTRATIVE_CHART)
    assert all(a["is_system_default"] for a in accounts)


def test_duplicate_code_rejected_within_framework(client):
    _register(client)
    org = _create_org(client, is_demo=True).json()

    dup = _post_account(client, org["id"], code=ILLUSTRATIVE_CHART[0]["code"])
    assert dup.status_code == 409


def test_same_code_allowed_in_different_framework(client):
    _register(client)
    ohada = _create_org(client, name="OHADA Co", framework="OHADA").json()
    ifrs = _create_org(client, name="IFRS Co", framework="IFRS").json()

    assert _post_account(client, ohada["id"], framework="OHADA", code="7777").status_code == 201
    assert _post_account(client, ifrs["id"], framework="IFRS", code="7777").status_code == 201


def test_custom_account_framework_must_match_org(client):
    _register(client)
    org = _create_org(client, framework="OHADA").json()

    resp = _post_account(client, org["id"], framework="IFRS", code="5555")
    assert resp.status_code == 400


def test_invalid_normal_balance_rejected(client):
    _register(client)
    org = _create_org(client, is_demo=True).json()

    resp = _post_account(client, org["id"], code="8888", normal_balance="banana")
    assert resp.status_code == 422


def test_account_list_scoped_per_organization(client):
    _register(client, "alice@example.com")
    alice_org = _create_org(client, is_demo=True).json()

    # Bob registers and cannot read Alice's chart (404, not 403).
    _register(client, "bob@example.com")
    resp = client.get(f"/accounts?organization_id={alice_org['id']}")
    assert resp.status_code == 404

    # Bob's own org has its own (empty, non-demo) chart.
    bob_org = _create_org(client, name="Bob Co", is_demo=False).json()
    resp = client.get(f"/accounts?organization_id={bob_org['id']}")
    assert resp.status_code == 200
    assert resp.json() == []


def test_patch_edits_name_and_toggles_active(client):
    _register(client)
    org = _create_org(client, is_demo=True).json()
    first = client.get(f"/accounts?organization_id={org['id']}").json()[0]

    resp = client.patch(
        f"/accounts/{first['id']}?organization_id={org['id']}",
        json={"name_en": "Renamed", "active": False},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name_en"] == "Renamed"
    assert body["active"] is False

    # Re-activate.
    resp = client.patch(
        f"/accounts/{first['id']}?organization_id={org['id']}",
        json={"active": True},
    )
    assert resp.json()["active"] is True


def test_cannot_deactivate_account_with_posted_transactions_placeholder(
    client, test_db_session
):
    """Deactivation rule is wired; the check passes today (no transactions yet).

    PLACEHOLDER: the `transactions` table does not exist until Session 6, so
    has_posted_transactions() returns False and deactivation succeeds. When
    transactions land, extend this test to assert a 409 when a posted
    transaction references the account.
    """
    _register(client)
    org = _create_org(client, is_demo=True).json()
    first = client.get(f"/accounts?organization_id={org['id']}").json()[0]

    # The rule helper currently reports no posted transactions (TODO Session 6).
    assert has_posted_transactions(test_db_session, first["id"]) is False

    resp = client.patch(
        f"/accounts/{first['id']}?organization_id={org['id']}",
        json={"active": False},
    )
    assert resp.status_code == 200
    assert resp.json()["active"] is False


def test_custom_account_is_not_system_default(client):
    _register(client)
    org = _create_org(client, is_demo=True).json()

    resp = _post_account(client, org["id"], code="6969")
    assert resp.status_code == 201
    assert resp.json()["is_system_default"] is False
    assert resp.json()["active"] is True


def test_unauthenticated_account_access_rejected(client):
    resp = client.get("/accounts?organization_id=1")
    assert resp.status_code == 401