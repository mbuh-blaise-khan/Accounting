"""Tests for the chart of accounts: OHADA real structure, IFRS template,
seed, CRUD, validation, authorization. (Session 5 + Session 6b.)"""
from app.accounting.ifrs_template import IFRS_TEMPLATE
from app.accounting.ohada_chart import OHADA_CHART
from app.models.account import Account
from app.services.account_service import (
    has_posted_transactions,
    seed_chart_for_organization,
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


def _accounts_map(client, org_id):
    resp = client.get(f"/accounts?organization_id={org_id}")
    assert resp.status_code == 200
    return {a["code"]: a for a in resp.json()}


def test_ohada_seed_produces_real_hierarchy(client, test_db_session):
    """The OHADA seed is hierarchical, all 9 classes present, parents linked."""
    _register(client)
    org = _create_org(client, framework="OHADA", is_demo=False).json()

    created = seed_chart_for_organization(test_db_session, org["id"])
    assert len(created) == len(OHADA_CHART)
    # Idempotent: a second run adds nothing.
    assert seed_chart_for_organization(test_db_session, org["id"]) == []

    rows = test_db_session.query(Account).all()
    by_code = {a.code: a for a in rows}
    assert len(by_code) == len(OHADA_CHART)

    # Every OHADA account carries its real class number 1-9.
    classes = {a.ohada_class_number for a in rows}
    assert classes == {1, 2, 3, 4, 5, 6, 7, 8, 9}

    # Parent pointers are valid within the same org and are real rows.
    for a in rows:
        assert a.is_system_default is True
        assert a.framework == "OHADA"
        if a.parent_account_id is not None:
            parent = test_db_session.get(Account, a.parent_account_id)
            assert parent is not None
            assert parent.organization_id == a.organization_id
            assert parent.code in by_code

    # Required sub-classes go >=3 levels deep (2 -> 3 -> 4 digit chains).
    for chain in (
        ("10", "101", "1011"),  # Capital
        ("21", "212", "2121"),  # Intangible fixed assets
        ("40", "401", "4011"),  # Suppliers
        ("41", "411", "4111"),  # Customers
        ("52", "521", "5211"),  # Banks
        ("57", "571", "5711"),  # Cash
        ("60", "601", "6011"),  # Purchases
        ("66", "661", "6611"),  # Personnel costs
        ("70", "701", "7011"),  # Sales
    ):
        parent = by_code[chain[0]]
        child = by_code[chain[1]]
        grandchild = by_code[chain[2]]
        assert child.parent_account_id == parent.id
        assert grandchild.parent_account_id == child.id


def test_ifrs_template_seeds_flat_and_editable(client):
    """IFRS workspace gets a flat editable template; no OHADA class numbers."""
    _register(client)
    org = _create_org(client, framework="IFRS", is_demo=True).json()

    accounts = client.get(f"/accounts?organization_id={org['id']}").json()
    assert len(accounts) == len(IFRS_TEMPLATE)
    assert all(a["ohada_class_number"] is None for a in accounts)
    assert all(a["is_system_default"] for a in accounts)
    # Template items are editable (it is a starting point the business adapts).
    first = accounts[0]
    resp = client.patch(
        f"/accounts/{first['id']}?organization_id={org['id']}",
        json={"name_en": "Cash (adapted)"},
    )
    assert resp.status_code == 200
    assert resp.json()["name_en"] == "Cash (adapted)"


def test_demo_org_auto_seeds_chart_per_framework(client):
    """Demo workspaces auto-seed the right structure for their framework."""
    _register(client)
    ohada = _create_org(client, framework="OHADA", is_demo=True).json()
    ifrs = _create_org(client, framework="IFRS", is_demo=True).json()

    ohada_accounts = client.get(f"/accounts?organization_id={ohada['id']}").json()
    ifrs_accounts = client.get(f"/accounts?organization_id={ifrs['id']}").json()
    assert len(ohada_accounts) == len(OHADA_CHART)
    assert len(ifrs_accounts) == len(IFRS_TEMPLATE)
    assert all(a["ohada_class_number"] is not None for a in ohada_accounts)
    assert all(a["ohada_class_number"] is None for a in ifrs_accounts)


def test_duplicate_code_rejected_within_framework(client):
    _register(client)
    org = _create_org(client, is_demo=True).json()

    dup = _post_account(client, org["id"], code=OHADA_CHART[0]["code"])
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


def test_cannot_deactivate_account_with_no_posted_transactions(
    client, test_db_session
):
    """An account with no posted transactions can be deactivated.

    The rule that blocks deactivation once posted transactions exist is covered
    in test_transactions.py (test_deactivate_account_blocked_after_posting).
    """
    _register(client)
    org = _create_org(client, is_demo=True).json()
    first = client.get(f"/accounts?organization_id={org['id']}").json()[0]

    # No transaction references this account yet -> the rule allows deactivation.
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

    resp = _post_account(client, org["id"], code="6969", ohada_class_number=6)
    assert resp.status_code == 201
    body = resp.json()
    assert body["is_system_default"] is False
    assert body["active"] is True
    # Custom OHADA accounts may carry the real class number too.
    assert body["ohada_class_number"] == 6


def test_unauthenticated_account_access_rejected(client):
    resp = client.get("/accounts?organization_id=1")
    assert resp.status_code == 401