"""Tests for Session 7: Journal and Cash Book read views.

Covers: only posted transactions appear; journal totals for a period equal the
sum of posted transaction lines in that period; filters (date range, account,
reference); the Cash Book shows only cash/bank movements; OHADA rows carry
account codes while IFRS rows omit them (Part B).
"""
from sqlalchemy import func

from app.models.enums import TransactionStatus
from app.models.transaction import Transaction, TransactionLine


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


def _accounts_by_name(client, org_id):
    resp = client.get(f"/accounts?organization_id={org_id}")
    assert resp.status_code == 200
    return {a["name_en"]: a for a in resp.json()}


def _create_account(client, org_id, code, name_en, name_fr):
    resp = client.post(
        "/accounts",
        json={
            "organization_id": org_id,
            "framework": "OHADA",
            "code": code,
            "name_en": name_en,
            "name_fr": name_fr,
            "account_class": "asset",
            "normal_balance": "debit",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


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


def _ohada_balanced(acc):
    return [
        {"account_id": acc["57"]["id"], "debit": 50000, "credit": 0, "narration": "Cash sale"},
        {"account_id": acc["70"]["id"], "debit": 0, "credit": 50000, "narration": "Sales"},
    ]


def _ifrs_balanced(acc):
    return [
        {"account_id": acc["Cash and cash equivalents"]["id"], "debit": 50000, "credit": 0},
        {"account_id": acc["Sales revenue"]["id"], "debit": 0, "credit": 50000},
    ]


def test_journal_shows_only_posted_transactions(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])

    draft = _make_txn(client, org["id"], _ohada_balanced(acc))
    posted = _make_txn(client, org["id"], _ohada_balanced(acc))
    _post(client, org["id"], posted["id"])

    resp = client.get(f"/journal-entries?organization_id={org['id']}")
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 2  # 2 lines, only for the posted transaction
    assert {r["transaction_id"] for r in rows} == {posted["id"]}
    assert draft["id"] not in {r["transaction_id"] for r in rows}

    # Row date is the real posted_at (Part C), present as the leading field.
    assert all(r["date"] is not None for r in rows)
    assert rows[0]["status"] == "posted"
    assert rows[0]["narration"] == "Cash sale"


def test_journal_totals_match_posted_lines_for_period(client, test_db_session):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])

    for _ in range(2):
        txn = _make_txn(client, org["id"], _ohada_balanced(acc))
        _post(client, org["id"], txn["id"])

    resp = client.get(
        f"/journal-entries?organization_id={org['id']}&from=2000-01-01&to=2100-01-01"
    )
    rows = resp.json()
    assert len(rows) == 4
    total_debit = sum(float(r["debit"]) for r in rows)
    total_credit = sum(float(r["credit"]) for r in rows)
    assert total_debit == total_credit == 100000

    # Cross-check against the DB: sum of posted-line debits in the same period.
    db_total = (
        test_db_session.query(func.sum(TransactionLine.debit_amount))
        .join(Transaction, Transaction.id == TransactionLine.transaction_id)
        .filter(
            Transaction.organization_id == org["id"],
            Transaction.status == TransactionStatus.posted,
        )
        .scalar()
    )
    assert float(db_total) == total_debit


def test_journal_filters_by_date_account_and_reference(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make_txn(client, org["id"], _ohada_balanced(acc))
    _post(client, org["id"], txn["id"])

    # Account filter -> only the Cash line.
    resp = client.get(
        f"/journal-entries?organization_id={org['id']}&account_id={acc['57']['id']}"
    )
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["account_code"] == "57"
    assert float(rows[0]["debit"]) == 50000

    # Reference filter -> matches ONLY the reference field (TX-####), not the
    # description or account name (Part A fix).
    ref = f"TX-{txn['id']:04d}"
    resp = client.get(f"/journal-entries?organization_id={org['id']}&reference={ref}")
    assert len(resp.json()) == 2
    # A word that only appears in the description must NOT match a reference.
    resp = client.get(f"/journal-entries?organization_id={org['id']}&reference=cash")
    assert resp.json() == []

    # Date range in the distant past -> nothing.
    resp = client.get(
        f"/journal-entries?organization_id={org['id']}&from=2000-01-01&to=2000-01-02"
    )
    assert resp.json() == []


def test_cash_book_only_shows_cash_bank_movements(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make_txn(client, org["id"], _ohada_balanced(acc))
    _post(client, org["id"], txn["id"])

    resp = client.get(f"/cashbook?organization_id={org['id']}")
    assert resp.status_code == 200
    rows = resp.json()
    # Only the Cash (57) movement — the Sales line is not a cash/bank movement.
    assert len(rows) == 1
    assert rows[0]["account_code"] == "57"
    assert rows[0]["account_id"] == acc["57"]["id"]


def test_journal_ohada_includes_codes_ifrs_omits_them(client):
    _register(client)

    # OHADA workspace: account numbers present (real SYSCOHADA layout).
    ohada = _create_demo_org(client, name="OHADA Co")
    acc = _accounts_by_code(client, ohada["id"])
    txn = _make_txn(client, ohada["id"], _ohada_balanced(acc))
    _post(client, ohada["id"], txn["id"])
    rows = client.get(f"/journal-entries?organization_id={ohada['id']}").json()
    assert len(rows) == 2
    assert {r["account_code"] for r in rows} == {"57", "70"}

    # IFRS workspace: no account numbers anywhere.
    ifrs = _create_demo_org(client, name="IFRS Co", framework="IFRS")
    iacc = _accounts_by_name(client, ifrs["id"])
    txn2 = _make_txn(client, ifrs["id"], _ifrs_balanced(iacc), description="IFRS cash sale")
    _post(client, ifrs["id"], txn2["id"])
    rows = client.get(f"/journal-entries?organization_id={ifrs['id']}").json()
    assert len(rows) == 2
    assert all(r["account_code"] is None for r in rows)
    assert {r["account_name_en"] for r in rows} == {
        "Cash and cash equivalents",
        "Sales revenue",
    }

    # IFRS Cash Book still finds the cash movement by name.
    cb = client.get(f"/cashbook?organization_id={ifrs['id']}").json()
    assert len(cb) == 1
    assert cb[0]["account_name_en"] == "Cash and cash equivalents"


def test_cash_book_single_excludes_bank_and_double_splits_types(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    bank = _create_account(client, org["id"], code="529", name_en="Bank account", name_fr="Compte banque")
    cash_txn = _make_txn(client, org["id"], _ohada_balanced(acc))
    _post(client, org["id"], cash_txn["id"])
    bank_txn = _make_txn(client, org["id"], [
        {"account_id": bank["id"], "debit": 200, "credit": 0},
        {"account_id": acc["70"]["id"], "debit": 0, "credit": 200},
    ])
    _post(client, org["id"], bank_txn["id"])

    single = client.get(f"/cashbook?organization_id={org['id']}&type=single").json()
    double = client.get(f"/cashbook?organization_id={org['id']}&type=double").json()
    assert single and all(row["cashbook_type"] == "cash" for row in single)
    assert {row["cashbook_type"] for row in double} == {"cash", "bank"}
    assert len(double) > len(single)
    assert sum(float(row["debit"]) for row in double if row["cashbook_type"] == "cash") == 50000
    assert sum(float(row["credit"]) for row in double if row["cashbook_type"] == "cash") == 0
    assert sum(float(row["debit"]) for row in double if row["cashbook_type"] == "bank") == 200
    assert sum(float(row["credit"]) for row in double if row["cashbook_type"] == "bank") == 0


def test_cash_book_type_preserves_filters_and_reversed_rows(client):
    _register(client)
    org = _create_demo_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make_txn(client, org["id"], _ohada_balanced(acc))
    _post(client, org["id"], txn["id"])
    rows = client.get(f"/cashbook?organization_id={org['id']}&type=single&from=2000-01-01&to=2000-01-02").json()
    assert rows == []
    assert client.get(f"/cashbook?organization_id={org['id']}&type=invalid").status_code == 422

    # A posted entry and its reversal remain visible as historical rows, but
    # each Cash Book amount column nets to zero in both layouts.
    reversal = client.post(f"/transactions/{txn['id']}/reverse?organization_id={org['id']}")
    assert reversal.status_code == 200, reversal.text
    single = client.get(f"/cashbook?organization_id={org['id']}&type=single").json()
    double = client.get(f"/cashbook?organization_id={org['id']}&type=double").json()
    assert len(single) == 2  # original cash line + mirrored reversal cash line
    assert sum(float(row["debit"]) for row in single) == sum(float(row["credit"]) for row in single)
    cash_rows = [row for row in double if row["cashbook_type"] == "cash"]
    assert sum(float(row["debit"]) for row in cash_rows) == sum(float(row["credit"]) for row in cash_rows)
    assert all(row["cashbook_type"] in {"cash", "bank"} for row in double)
