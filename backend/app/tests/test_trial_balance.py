"""Trial Balance tests (Session 9).

Covers the acceptance points: closing debit total == closing credit total
across seeded scenarios at ALL three column views; a reversed pair nets to
zero; opening + movement == closing on a real account (using a backdated
entry via the shared test session); period filtering; zero-activity accounts
are omitted; OHADA rows carry account numbers while IFRS rows don't.
"""
from datetime import date, datetime, timedelta, timezone


def _today_utc() -> date:
    """Today's date on the UTC clock.

    Trial-balance date bounds are interpreted as UTC day boundaries (the
    service stores/filters on UTC `posted_at`), so the tests must derive
    "today" from UTC too — using the local clock would make bounds race the
    postings whenever the local date is ahead of the UTC date (e.g. after
    local midnight in a UTC+ timezone).
    """
    return datetime.now(timezone.utc).date()


def _register(client, email="tb@example.com"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "display_name": "Tb",
            "language_preference": "en",
        },
    )


def _create_org(client, framework="OHADA", name="TB Co"):
    return client.post(
        "/organizations",
        json={"name": name, "framework": framework, "currency": "XAF", "is_demo": True},
    ).json()


def _accounts_by_code(client, org_id):
    return {a["code"]: a for a in client.get(f"/accounts?organization_id={org_id}").json()}


def _post_txn(client, org_id, acc_d, acc_c, amount, description="TB entry"):
    r = client.post(
        "/transactions",
        json={
            "organization_id": org_id,
            "description": description,
            "lines": [
                {"account_id": acc_d["id"], "debit": amount, "credit": 0},
                {"account_id": acc_c["id"], "debit": 0, "credit": amount},
            ],
        },
    )
    assert r.status_code in (200, 201), r.text
    txn = r.json()
    p = client.post(f"/transactions/{txn['id']}/post?organization_id={org_id}")
    assert p.status_code == 200, p.text
    return txn


def _tb(client, org_id, **params):
    qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
    url = f"/trial-balance?organization_id={org_id}" + (f"&{qs}" if qs else "")
    r = client.get(url)
    assert r.status_code == 200, r.text
    return r.json()


def test_closing_totals_balance_at_all_column_views(client):
    """Several balanced transactions -> closing Dr total == Cr total, and the
    `columns` parameter never changes the data (it is only a view hint)."""
    _register(client)
    org = _create_org(client)
    acc = _accounts_by_code(client, org["id"])
    _post_txn(client, org["id"], acc["57"], acc["70"], 10000, "Cash sale A")
    _post_txn(client, org["id"], acc["57"], acc["70"], 2500, "Cash sale B")
    _post_txn(client, org["id"], acc["60"], acc["57"], 4000, "Buy supplies")

    tb2 = _tb(client, org["id"], columns=2)
    tb4 = _tb(client, org["id"], columns=4)
    tb6 = _tb(client, org["id"], columns=6)

    for tb in (tb2, tb4, tb6):
        t = tb["totals"]
        assert float(t["closing_debit"]) == float(t["closing_credit"])
        assert tb["balanced"] is True
    # The payload is view-independent:
    assert tb2["rows"] == tb4["rows"] == tb6["rows"]
    # Real arithmetic: cash net closing (10000+2500-4000) appears as Dr 8500.
    cash_row = next(r for r in tb2["rows"] if r["code"] == "57")
    assert float(cash_row["closing_debit"]) == 8500.0


def test_reversed_pair_nets_to_zero_and_counts_as_history(client):
    """Posted transaction + its reversal: totals still balance and the account
    returns to its pre-entry balance; both legs count within the period."""
    _register(client)
    org = _create_org(client)
    acc = _accounts_by_code(client, org["id"])
    _post_txn(client, org["id"], acc["57"], acc["70"], 5000, "Sale to reverse")

    before = _tb(client, org["id"])
    listed = client.get(f"/transactions?organization_id={org['id']}").json()
    posted = [t for t in listed if t["status"] == "posted"]
    rev = client.post(
        f"/transactions/{posted[-1]['id']}/reverse?organization_id={org['id']}"
    )
    assert rev.status_code == 200

    after = _tb(client, org["id"])
    assert after["balanced"] is True
    # Net effect of original + mirror = zero: every account back to nil.
    assert len(after["rows"]) == 0 or all(
        float(r["closing_debit"]) == 0.0 and float(r["closing_credit"]) == 0.0
        for r in after["rows"]
    )

    # History check: bound the period to today so BOTH legs land in movement,
    # and the pair must cancel inside the movement totals too.
    today = _today_utc().isoformat()
    moved = _tb(client, org["id"], **{"from": today})
    assert moved["balanced"] is True
    mv_dr = float(moved["totals"]["movement_debit"])
    mv_cr = float(moved["totals"]["movement_credit"])
    # Two entries × one side each = 10000 of movement on both sides.
    assert mv_dr == mv_cr == 10000.0


def test_opening_plus_movement_equals_closing_with_backdated_entry(client, test_db_session):
    """A backdated entry lands in OPENING; this month's entry in MOVEMENT;
    closing is their exact combination — verified per real account row."""
    from app.models.transaction import Transaction

    _register(client)
    org = _create_org(client)
    acc = _accounts_by_code(client, org["id"])

    old = _post_txn(client, org["id"], acc["57"], acc["70"], 7000, "Old sale")
    _post_txn(client, org["id"], acc["57"], acc["70"], 1200, "New sale")

    # Backdate the first posting to the 1st of last month (test-only write).
    past = _today_utc() - timedelta(days=35)
    row = test_db_session.get(Transaction, old["id"])
    row.posted_at = row.posted_at.replace(year=past.year, month=past.month, day=past.day)
    test_db_session.commit()

    month_start = _today_utc().replace(day=1).isoformat()
    tb = _tb(client, org["id"],
             **{"as_of": _today_utc().isoformat(), "from": month_start})

    cash = next(r for r in tb["rows"] if r["code"] == acc["57"]["code"])
    sales = next(r for r in tb["rows"] if r["code"] == acc["70"]["code"])
    # Opening carries ONLY the backdated entry.
    assert float(cash["opening_debit"]) == 7000.0
    assert float(sales["opening_credit"]) == 7000.0
    # Movement carries ONLY this month's activity.
    assert float(cash["movement_debit"]) == 1200.0
    assert float(sales["movement_credit"]) == 1200.0
    # Closing = opening + movement.
    assert float(cash["closing_debit"]) == 8200.0
    assert float(sales["closing_credit"]) == 8200.0
    assert float(tb["totals"]["closing_debit"]) == float(tb["totals"]["closing_credit"])
    assert tb["balanced"] is True


def test_period_filtering_excludes_entries_after_as_of(client, test_db_session):
    """as_of BEFORE a posting excludes it from every column entirely."""
    from app.models.transaction import Transaction

    _register(client)
    org = _create_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _post_txn(client, org["id"], acc["57"], acc["70"], 900, "Future entry")

    tomorrow = _today_utc() + timedelta(days=1)
    row = test_db_session.get(Transaction, txn["id"])
    row.posted_at = row.posted_at.replace(
        year=tomorrow.year, month=tomorrow.month, day=tomorrow.day
    )
    test_db_session.commit()

    past_bound = (_today_utc() - timedelta(days=10)).isoformat()
    tb = _tb(client, org["id"], **{"as_of": past_bound})
    used_ids = {r["account_id"] for r in tb["rows"]}
    assert acc["57"]["id"] not in used_ids
    assert float(tb["totals"]["closing_debit"]) == float(tb["totals"]["closing_credit"])


def test_zero_activity_accounts_are_omitted(client):
    """Documented decision: accounts with no included activity at ALL three
    levels do not appear as zero rows."""
    _register(client)
    org = _create_org(client)
    acc = _accounts_by_code(client, org["id"])
    _post_txn(client, org["id"], acc["57"], acc["70"], 3000, "Only two accounts")

    tb = _tb(client, org["id"])
    codes = {r["code"] for r in tb["rows"]}
    untouched = [c for c in acc if c not in ("57", "70")]
    assert all(c not in codes for c in untouched)
    assert "57" in codes and "70" in codes


def test_ohada_rows_have_codes_ifrs_rows_do_not(client):
    _register(client)
    ohada = _create_org(client, framework="OHADA", name="OH Co")
    acc_o = _accounts_by_code(client, ohada["id"])
    _post_txn(client, ohada["id"], acc_o["57"], acc_o["70"], 4500, "OHADA sale")
    tb_o = _tb(client, ohada["id"])
    assert tb_o["rows"]
    assert all(r["code"] for r in tb_o["rows"])

    ifrs = _create_org(client, framework="IFRS", name="IF Co")
    ifrs_accounts = client.get(f"/accounts?organization_id={ifrs['id']}").json()
    by_name = {a["name_en"].lower(): a for a in ifrs_accounts}
    cash = next(a for n, a in by_name.items() if "cash" in n)
    revenue = next(a for n, a in by_name.items() if "revenue" in n or "sales" in n)
    _post_txn(client, ifrs["id"], cash, revenue, 2100, "IFRS sale")
    tb_i = _tb(client, ifrs["id"])
    assert tb_i["rows"]
    assert all(r["code"] is None for r in tb_i["rows"])


def test_invalid_columns_rejected(client):
    _register(client)
    org = _create_org(client)
    r = client.get(f"/trial-balance?organization_id={org['id']}&columns=3")
    assert r.status_code == 422


def test_unauthenticated_trial_balance_rejected(client):
    r = client.get("/trial-balance?organization_id=1")
    assert r.status_code in (401, 403)
