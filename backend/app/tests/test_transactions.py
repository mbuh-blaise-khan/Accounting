"""Tests for Session 6: first transaction entry and posting.

Covers draft creation, the service-layer balance rule, immutability, the
reversal stub, active-account validation, org scoping, and the deactivation
guard that posting enables.
"""
import pytest
from fastapi import HTTPException

from app.models.user import User
from app.services import transaction_service


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


def _login(client, email="alice@example.com", password="supersecret123"):
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()


def _create_demo_org(client, name="Acme", framework="OHADA"):
    resp = client.post(
        "/organizations",
        json={"name": name, "framework": framework, "currency": "XAF", "is_demo": True},
    )
    assert resp.status_code == 201
    return resp.json()


def _accounts_by_code(client, org_id):
    resp = client.get(f"/accounts?organization_id={org_id}")
    assert resp.status_code == 200
    return {a["code"]: a for a in resp.json()}


def _make_txn(client, org_id, lines, description="Sold goods for cash"):
    return client.post(
        "/transactions",
        json={"organization_id": org_id, "description": description, "lines": lines},
    )


def _balanced_lines(acc):
    """A classic example: debit Cash 50,000, credit Sales 50,000."""
    return [
        {"account_id": acc["57"]["id"], "debit": 50000, "credit": 0},
        {"account_id": acc["70"]["id"], "debit": 0, "credit": 50000},
    ]


def test_create_draft_transaction(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])

    resp = _make_txn(client, org["id"], _balanced_lines(acc))
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "draft"
    assert body["description"] == "Sold goods for cash"
    assert len(body["lines"]) == 2
    assert body["posted_at"] is None


def test_balanced_transaction_posts_successfully(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])

    txn = _make_txn(client, org["id"], _balanced_lines(acc)).json()
    resp = client.post(f"/transactions/{txn['id']}/post?organization_id={org['id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "posted"
    assert body["posted_at"] is not None


def test_unbalanced_transaction_cannot_be_posted(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])

    unbalanced = [
        {"account_id": acc["57"]["id"], "debit": 50000, "credit": 0},
        {"account_id": acc["70"]["id"], "debit": 0, "credit": 40000},
    ]
    txn = _make_txn(client, org["id"], unbalanced).json()

    # Enforced at the SERVICE layer, not just the UI.
    resp = client.post(f"/transactions/{txn['id']}/post?organization_id={org['id']}")
    assert resp.status_code == 400
    assert "balanced" in resp.json()["detail"].lower()


def test_transaction_needs_at_least_two_lines(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])

    resp = _make_txn(
        client, org["id"], [{"account_id": acc["57"]["id"], "debit": 100, "credit": 0}]
    )
    assert resp.status_code == 422


def test_line_cannot_be_both_sides_or_neither(client):
    """A line must be a debit OR a credit, never both (or neither)."""
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])

    resp = _make_txn(
        client,
        org["id"],
        [
            {"account_id": acc["57"]["id"], "debit": 100, "credit": 0},
            {"account_id": acc["70"]["id"], "debit": 100, "credit": 100},
        ],
    )
    assert resp.status_code == 422


def test_lines_must_reference_known_and_active_accounts(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])

    # Unknown account -> rejected.
    resp = _make_txn(
        client,
        org["id"],
        [
            {"account_id": 999999, "debit": 100, "credit": 0},
            {"account_id": acc["70"]["id"], "debit": 0, "credit": 100},
        ],
    )
    assert resp.status_code == 422

    # Inactive account -> rejected.
    first = acc["57"]
    client.patch(
        f"/accounts/{first['id']}?organization_id={org['id']}", json={"active": False}
    )
    resp = _make_txn(
        client,
        org["id"],
        [
            {"account_id": first["id"], "debit": 100, "credit": 0},
            {"account_id": acc["70"]["id"], "debit": 0, "credit": 100},
        ],
    )
    assert resp.status_code == 422
    assert "inactive" in resp.json()["detail"].lower()


def test_posted_transaction_cannot_be_posted_again(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make_txn(client, org["id"], _balanced_lines(acc)).json()

    assert (
        client.post(f"/transactions/{txn['id']}/post?organization_id={org['id']}")
    ).status_code == 200
    again = client.post(f"/transactions/{txn['id']}/post?organization_id={org['id']}")
    assert again.status_code == 409


def test_posted_transaction_is_immutable_guard(client, test_db_session):
    """No edit/delete path exists; the immutability guard rejects posted rows."""
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make_txn(client, org["id"], _balanced_lines(acc)).json()
    client.post(f"/transactions/{txn['id']}/post?organization_id={org['id']}")

    db = test_db_session
    user = db.query(User).filter(User.email == "alice@example.com").one()
    posted = transaction_service.get_transaction(db, user, org["id"], txn["id"])

    with pytest.raises(HTTPException) as exc:
        transaction_service.assert_editable(posted)
    assert exc.value.status_code == 409

    # A draft is still editable.
    draft_id = _make_txn(client, org["id"], _balanced_lines(acc)).json()["id"]
    draft = transaction_service.get_transaction(db, user, org["id"], draft_id)
    transaction_service.assert_editable(draft)  # no raise


def test_reverse_posted_transaction(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make_txn(client, org["id"], _balanced_lines(acc)).json()
    client.post(f"/transactions/{txn['id']}/post?organization_id={org['id']}")

    # Reversal now returns the NEW mirrored, posted entry (not the original).
    resp = client.post(f"/transactions/{txn['id']}/reverse?organization_id={org['id']}")
    assert resp.status_code == 200
    mirror = resp.json()
    assert mirror["status"] == "posted"
    assert mirror["reverse_of_id"] == txn["id"]

    # The original is marked reversed (never edited/deleted).
    listed = {t["id"]: t for t in client.get(f"/transactions?organization_id={org['id']}").json()}
    assert listed[txn["id"]]["status"] == "reversed"


def test_draft_cannot_be_reversed(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make_txn(client, org["id"], _balanced_lines(acc)).json()

    resp = client.post(f"/transactions/{txn['id']}/reverse?organization_id={org['id']}")
    assert resp.status_code == 409


def test_reversed_transaction_cannot_be_reversed_again(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make_txn(client, org["id"], _balanced_lines(acc)).json()
    client.post(f"/transactions/{txn['id']}/post?organization_id={org['id']}")
    client.post(f"/transactions/{txn['id']}/reverse?organization_id={org['id']}")

    resp = client.post(f"/transactions/{txn['id']}/reverse?organization_id={org['id']}")
    assert resp.status_code == 409


def test_transactions_list_scoped_per_organization(client):
    _register(client, "alice@example.com")
    alice_org = _create_demo_org(client)
    acc = _accounts_by_code(client, alice_org["id"])
    txn = _make_txn(client, alice_org["id"], _balanced_lines(acc)).json()

    # Bob cannot see Alice's transaction list (404, not 403).
    _register(client, "bob@example.com")
    resp = client.get(f"/transactions?organization_id={alice_org['id']}")
    assert resp.status_code == 404

    # Bob's own (non-demo) org has an empty list.
    bob_org = client.post(
        "/organizations",
        json={"name": "Bob Co", "framework": "OHADA", "currency": "XAF", "is_demo": False},
    ).json()
    resp = client.get(f"/transactions?organization_id={bob_org['id']}")
    assert resp.status_code == 200
    assert resp.json() == []

    # Log back in as Alice to read her own transaction list.
    _login(client, "alice@example.com")  # sets alice's cookie again
    resp = client.get(f"/transactions?organization_id={alice_org['id']}")
    ids = [t["id"] for t in resp.json()]
    assert txn["id"] in ids


def test_deactivate_account_blocked_after_posting(client):
    """Once an account is used in a posted transaction it cannot be deactivated."""
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    _make_txn(client, org["id"], _balanced_lines(acc))
    txn = client.get(f"/transactions?organization_id={org['id']}").json()[0]
    client.post(f"/transactions/{txn['id']}/post?organization_id={org['id']}")

    cash = acc["57"]
    resp = client.patch(
        f"/accounts/{cash['id']}?organization_id={org['id']}", json={"active": False}
    )
    assert resp.status_code == 409
    assert "posted transactions" in resp.json()["detail"].lower()


def test_draft_reference_does_not_block_deactivation(client):
    """An account only in a DRAFT transaction can still be deactivated."""
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    _make_txn(client, org["id"], _balanced_lines(acc))  # stays draft

    cash = acc["57"]
    resp = client.patch(
        f"/accounts/{cash['id']}?organization_id={org['id']}", json={"active": False}
    )
    assert resp.status_code == 200
    assert resp.json()["active"] is False


def test_unauthenticated_transaction_access_rejected(client):
    resp = client.get("/transactions?organization_id=1")
    assert resp.status_code == 401