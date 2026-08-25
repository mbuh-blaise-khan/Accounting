"""Tests for Session 8: General Ledger service + endpoint.

Covers: the closing-balance identity (closing = opening +/- net movements per
the account's normal balance), the credit-normal convention for revenue
accounts, opening respecting the `from` bound, no-activity accounts showing
opening == closing, drafts never appearing, and org scoping (404).
"""
from datetime import datetime, timezone

from app.models.transaction import Transaction


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
    resp = client.post(
        "/transactions",
        json={"organization_id": org_id, "description": description, "lines": lines},
    )
    assert resp.status_code == 201
    return resp.json()


def _post(client, org_id, txn_id):
    resp = client.post(f"/transactions/{txn_id}/post?organization_id={org_id}")
    assert resp.status_code == 200
    return resp.json()


def _ledger(client, org_id, account_id, query=""):
    return client.get(f"/ledger/{account_id}?organization_id={org_id}{query}")


def _sale(acc):
    """Debit Cash 50,000 / credit Sales 50,000."""
    return [
        {"account_id": acc["57"]["id"], "debit": 50000, "credit": 0},
        {"account_id": acc["70"]["id"], "debit": 0, "credit": 50000},
    ]


def _cash_purchase(acc):
    """Debit Purchases 20,000 / credit Cash 20,000 (paid from cash)."""
    return [
        {"account_id": acc["60"]["id"], "debit": 20000, "credit": 0},
        {"account_id": acc["57"]["id"], "debit": 0, "credit": 20000},
    ]


def _set_posted_at(test_db_session, txn_id, when):
    """Re-date a posted transaction so period boundaries can be exercised."""
    row = test_db_session.get(Transaction, txn_id)
    assert row is not None
    row.posted_at = when
    test_db_session.commit()


def test_ledger_debit_normal_identity(client):
    """Cash (debit-normal): closing = opening + debit_movements - credit_movements."""
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    _post(client, org["id"], _make_txn(client, org["id"], _sale(acc))["id"])
    _post(
        client,
        org["id"],
        _make_txn(client, org["id"], _cash_purchase(acc), "Bought goods")["id"],
    )

    resp = _ledger(client, org["id"], acc["57"]["id"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["account"]["id"] == acc["57"]["id"]
    assert body["account"]["code"] == "57"
    assert body["account"]["normal_balance"] == "debit"
    assert float(body["opening_balance"]) == 0
    assert float(body["debit_movements"]) == 50000
    assert float(body["credit_movements"]) == 20000
    # THE IDENTITY under test.
    assert float(body["closing_balance"]) == (
        float(body["opening_balance"])
        + float(body["debit_movements"])
        - float(body["credit_movements"])
    )
    assert float(body["closing_balance"]) == 30000
    # Chronological movements whose running balance ends at the closing figure.
    assert [m["reference"] for m in body["movements"]] == ["TX-0001", "TX-0002"]
    assert float(body["movements"][0]["running_balance"]) == 50000
    assert float(body["movements"][-1]["running_balance"]) == 30000
    assert all(m["date"] is not None for m in body["movements"])


def test_ledger_credit_normal_convention(client):
    """Sales (credit-normal): closing = opening + credit_movements - debit_movements."""
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    _post(client, org["id"], _make_txn(client, org["id"], _sale(acc))["id"])

    resp = _ledger(client, org["id"], acc["70"]["id"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["account"]["normal_balance"] == "credit"
    assert float(body["opening_balance"]) == 0
    assert float(body["debit_movements"]) == 0
    assert float(body["credit_movements"]) == 50000
    assert float(body["closing_balance"]) == (
        float(body["opening_balance"])
        + float(body["credit_movements"])
        - float(body["debit_movements"])
    )
    assert float(body["closing_balance"]) == 50000


def test_ledger_opening_respects_from_bound(client, test_db_session):
    """Activity before `from` lands in OPENING only; movements exclude it."""
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    t1 = _make_txn(client, org["id"], _sale(acc))
    t2 = _make_txn(client, org["id"], _cash_purchase(acc), "Bought goods")
    _post(client, org["id"], t1["id"])
    _post(client, org["id"], t2["id"])

    # Re-date: t1 on Jan 5 (before the window), t2 on Jan 10 (inside it).
    _set_posted_at(
        test_db_session, t1["id"], datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc)
    )
    _set_posted_at(
        test_db_session, t2["id"], datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    )

    resp = _ledger(
        client,
        org["id"],
        acc["57"]["id"],
        query="&from=2026-01-06&to=2026-01-28",
    )
    assert resp.status_code == 200
    body = resp.json()
    # Opening carries the pre-period sale; movements carry only the purchase.
    assert float(body["opening_balance"]) == 50000
    assert [m["reference"] for m in body["movements"]] == ["TX-0002"]
    assert float(body["debit_movements"]) == 0
    assert float(body["credit_movements"]) == 20000
    assert float(body["closing_balance"]) == 30000
    assert float(body["movements"][0]["running_balance"]) == 30000
    assert body["date_from"] == "2026-01-06"
    assert body["date_to"] == "2026-01-28"


def test_ledger_no_activity_shows_opening_equal_closing(client):
    """An untouched account: opening == closing == 0 with an empty movement list."""
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])

    resp = _ledger(client, org["id"], acc["21"]["id"])
    assert resp.status_code == 200
    body = resp.json()
    assert body["movements"] == []
    assert float(body["opening_balance"]) == 0
    assert float(body["closing_balance"]) == 0

    # Same holds inside an explicit period.
    resp = _ledger(
        client, org["id"], acc["21"]["id"], query="&from=2026-01-01&to=2026-01-31"
    )
    body = resp.json()
    assert body["movements"] == []
    assert float(body["opening_balance"]) == float(body["closing_balance"]) == 0


def test_ledger_excludes_draft_transactions(client):
    """Drafts never appear — only POSTED journal lines feed the ledger."""
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    draft = _make_txn(client, org["id"], _sale(acc))  # stays draft
    posted = _make_txn(client, org["id"], _sale(acc))
    _post(client, org["id"], posted["id"])

    body = _ledger(client, org["id"], acc["57"]["id"]).json()
    assert {m["transaction_id"] for m in body["movements"]} == {posted["id"]}
    assert draft["id"] not in {m["transaction_id"] for m in body["movements"]}
    assert float(body["closing_balance"]) == 50000


def test_ledger_scoped_per_organization(client):
    """A non-member gets 404; another workspace's account id is not readable."""
    _register(client, "alice@example.com")
    alice_org = _create_demo_org(client, name="Alice Co")
    acc = _accounts_by_code(client, alice_org["id"])
    _post(client, alice_org["id"], _make_txn(client, alice_org["id"], _sale(acc))["id"])

    _register(client, "bob@example.com")
    # Bob is not a member of Alice's org -> 404 (not 403).
    resp = _ledger(client, alice_org["id"], acc["57"]["id"])
    assert resp.status_code == 404

    # An account belonging to another org is rejected for Bob's own org too.
    bob_org = _create_demo_org(client, name="Bob Co")
    bob_acc = _accounts_by_code(client, bob_org["id"])
    resp = _ledger(client, bob_org["id"], acc["57"]["id"])
    assert resp.status_code == 404

    # Unauthenticated requests are rejected outright.
    client.cookies.clear()
    resp = _ledger(client, bob_org["id"], bob_acc["57"]["id"])
    assert resp.status_code == 401