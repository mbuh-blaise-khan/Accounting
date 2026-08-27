"""Tests for the completed transaction-reversal workflow (post-Session-8 Part 4)
and the smart-ordered General Ledger account selector (Part 2).

Reversal rules under test:
- reversing a posted transaction creates a correctly mirrored entry (sides
  swapped), linked back to the original via reverse_of_id, and posts it;
- the original is marked `reversed` but its lines are never altered;
- drafts and already-reversed transactions are rejected;
- an original + its reversal net to zero in the ledger (both appear).

Also: the /accounts/suggested summary lists this member's custom accounts
first, then accounts with the most recent posted activity.
"""


def _register(client, email="rev@example.com"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "display_name": "Rev",
            "language_preference": "en",
        },
    )


def _create_ohada_org(client, name="RevCo"):
    return client.post(
        "/organizations",
        json={"name": name, "framework": "OHADA", "currency": "XAF", "is_demo": True},
    ).json()


def _accounts_by_code(client, org_id):
    return {a["code"]: a for a in client.get(f"/accounts?organization_id={org_id}").json()}


def _make(client, org_id, lines, description="Sold goods for cash"):
    return client.post(
        "/transactions",
        json={"organization_id": org_id, "description": description, "lines": lines},
    )


def _post(client, org_id, txn_id):
    r = client.post(f"/transactions/{txn_id}/post?organization_id={org_id}")
    assert r.status_code == 200, r.text
    return r.json()


def _balanced(acc):
    return [
        {"account_id": acc["57"]["id"], "debit": 5000, "credit": 0, "narration": "Cash"},
        {"account_id": acc["70"]["id"], "debit": 0, "credit": 5000, "narration": "Sales"},
    ]


def test_reverse_creates_mirrored_posted_entry_linked_to_original(client):
    _register(client)
    org = _create_ohada_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make(client, org["id"], _balanced(acc)).json()
    _post(client, org["id"], txn["id"])

    r = client.post(f"/transactions/{txn['id']}/reverse?organization_id={org['id']}")
    assert r.status_code == 200, r.text
    rev = r.json()

    # Mirror is posted and linked back to the original.
    assert rev["status"] == "posted"
    assert rev["reverse_of_id"] == txn["id"]
    assert rev["description"] == f"Reversal of {txn['description']}"

    # Sides are swapped exactly.
    orig_lines = {
        l["account_id"]: (float(l["debit_amount"]), float(l["credit_amount"]))
        for l in txn["lines"]
    }
    assert len(rev["lines"]) == 2
    for l in rev["lines"]:
        o = orig_lines[l["account_id"]]
        # mirrored: debit becomes the original's credit and vice-versa.
        assert (float(l["debit_amount"]), float(l["credit_amount"])) == (o[1], o[0])

    # Original is marked reversed but untouched.
    r = client.get(f"/transactions?organization_id={org['id']}")
    by_id = {t["id"]: t for t in r.json()}
    assert by_id[txn["id"]]["status"] == "reversed"
    oset = {(l["account_id"], float(l["debit_amount"]), float(l["credit_amount"])) for l in by_id[txn["id"]]["lines"]}
    nset = {(l["account_id"], float(l["debit_amount"]), float(l["credit_amount"])) for l in txn["lines"]}
    assert oset == nset


def test_reverse_rejects_draft_and_already_reversed(client):
    _register(client)
    org = _create_ohada_org(client)
    acc = _accounts_by_code(client, org["id"])

    # Draft cannot be reversed.
    draft = _make(client, org["id"], _balanced(acc)).json()
    r = client.post(f"/transactions/{draft['id']}/reverse?organization_id={org['id']}")
    assert r.status_code == 409

    # Posted then reversed.
    post = _make(client, org["id"], _balanced(acc)).json()
    _post(client, org["id"], post["id"])
    client.post(f"/transactions/{post['id']}/reverse?organization_id={org['id']}")
    # Already-reversed original cannot be reversed again.
    r = client.post(f"/transactions/{post['id']}/reverse?organization_id={org['id']}")
    assert r.status_code == 409


def test_reversal_net_zero_ledger(client):
    _register(client)
    org = _create_ohada_org(client)
    acc = _accounts_by_code(client, org["id"])
    txn = _make(client, org["id"], _balanced(acc)).json()
    _post(client, org["id"], txn["id"])
    client.post(f"/transactions/{txn['id']}/reverse?organization_id={org['id']}")

    # Cash ledger: original debit 5000 + reversal credit 5000 => closing 0.
    lr = client.get(f"/ledger/{acc['57']['id']}?organization_id={org['id']}")
    assert lr.status_code == 200
    body = lr.json()
    assert len(body["movements"]) == 2
    assert float(body["opening_balance"]["debit"]) == 0
    assert float(body["closing_balance"]["debit"]) == 0
    assert float(body["closing_balance"]["credit"]) == 0

    # Journal shows BOTH the reversed original and its posted reversal.
    rows = client.get(f"/journal-entries?organization_id={org['id']}").json()
    assert len(rows) == 4  # 2 lines origin + 2 lines reversal
    ids = {r["transaction_id"] for r in rows}
    assert txn["id"] in ids
    assert (txn["id"], "reversed") in {(r["transaction_id"], r["status"]) for r in rows}


def test_suggested_orders_custom_first_then_recent(client):
    _register(client)
    org = _create_ohada_org(client)
    acc = _accounts_by_code(client, org["id"])

    # Create a custom account (this member) -> must sort first, marked mine.
    r = client.post("/accounts", json={
        "organization_id": org["id"], "framework": "OHADA", "code": "9980",
        "name_en": "My Special Account", "name_fr": "Mon compte",
        "account_class": "asset", "normal_balance": "debit",
    })
    assert r.status_code == 201, r.text
    custom_id = r.json()["id"]

    # Two postings, both touching Cash (57); the second is the most recent.
    _post(client, org["id"], _make(client, org["id"], _balanced(acc)).json()["id"])
    _post(client, org["id"], _make(client, org["id"], _balanced(acc), description="Cash sale two").json()["id"])

    resp = client.get(f"/accounts/suggested?organization_id={org['id']}")
    assert resp.status_code == 200
    items = resp.json()
    ids = [i["id"] for i in items]

    assert ids[0] == custom_id
    assert items[0]["is_mine"] is True
    # The most-recently-used account (Cash 57) sorts before Sales (70).
    assert ids.index(acc["57"]["id"]) < ids.index(acc["70"]["id"])