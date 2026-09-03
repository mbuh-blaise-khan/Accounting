"""Financial-statement tests (Session 10, Part A).

Covers:
  1. OHADA Bilan balances (assets == liabilities + equity) for a known
     seeded scenario, with correct OHADA document labels.
  2. IFRS Statement of Financial Position balances for the parallel case.
  3. OHADA income statement (Compte de résultat) ordinary result matches
     revenue-class (7) totals minus expense-class (6) totals, and a class-8
     (HAO) entry appears in a SEPARATE result section, NOT blended into
     ordinary result.
  4. A reversed transaction + its mirror BOTH contribute, so the pair nets
     to zero on BOTH statements; and a draft transaction is never counted.
"""
from datetime import date, datetime, timezone
from decimal import Decimal


def _register(client, email="fs@example.com", name="FS"):
    r = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "display_name": name,
            "language_preference": "en",
        },
    )
    assert r.status_code in (200, 201), r.text
    return r.json()


def _create_org(client, framework="OHADA", name="FS Co"):
    r = client.post(
        "/organizations",
        json={"name": name, "framework": framework, "currency": "XAF", "is_demo": True},
    )
    assert r.status_code in (200, 201), r.text
    return r.json()


def _accounts_by_code(client, org_id):
    return {a["code"]: a for a in client.get(f"/accounts?organization_id={org_id}").json()}


def _post_txn(client, org_id, acc_d, acc_c, amount, description="entry"):
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


def _reverse(client, org_id, txn_id):
    r = client.post(f"/transactions/{txn_id}/reverse?organization_id={org_id}")
    assert r.status_code == 200, r.text
    return r.json()


def test_ohada_bilan_balances_and_has_correct_labels(client):
    """A simple balanced OHADA scenario: the Bilan must satisfy
    assets == liabilities + equity, with the OHADA document labels and
    closing balances derived purely from posted lines."""
    _register(client)
    org = _create_org(client, framework="OHADA")
    acc = _accounts_by_code(client, org["id"])

    # 1) Owner cash injection: Cash(5711) Dr 10000, Capital(10) Cr 10000
    _post_txn(client, org["id"], acc["5711"], acc["10"], 10000, "Owner capital")
    # 2) Borrowing: Cash(5711) Dr 3000, Borrowings(16) Cr 3000
    _post_txn(client, org["id"], acc["5711"], acc["16"], 3000, "Bank loan")

    # Closing: assets=Cash 13000 ; liabilities=Borrowings 3000 ;
    #          equity=Capital 10000 -> 13000 == 3000 + 10000
    fs = client.get(f"/reports/financial-position?organization_id={org['id']}")
    assert fs.status_code == 200, fs.text
    body = fs.json()
    assert body["framework"] == "OHADA"
    # OHADA: LEGAL document names — identical in BOTH UI languages, like "SARL"
    # which is never rendered as "LLC". Never translated.
    assert body["statement_name_en"] == "Bilan (OHADA)"
    assert body["statement_name_fr"] == "Bilan (OHADA)"
    assert body["statement_name_en"] == body["statement_name_fr"]
    assert body["currency"] == "XAF"
    assert body["balanced"] is True
    # Drill-down data (Session 10 Part B): every statement line carries its
    # account_id so the frontend can open that account's General Ledger.
    for section in body["sections"]:
        for line in section["lines"]:
            assert isinstance(line["account_id"], int) and line["account_id"] > 0
    assert float(body["assets"]) == 13000.0
    assert float(body["liabilities"]) == 3000.0
    assert float(body["equity"]) == 10000.0


def test_ifrs_financial_position_balances_and_has_correct_labels(client):
    """Parallel IFRS scenario: assets == liabilities + equity, with the
    IFRS document labels. IFRS accounts carry no code, so they are looked
    up by name."""
    _register(client)
    org = _create_org(client, framework="IFRS")
    accounts = client.get(f"/accounts?organization_id={org['id']}").json()
    by_name = {a["name_en"]: a for a in accounts}

    # 1) Owner cash injection: Cash Dr 10000, Share capital Cr 10000
    _post_txn(client, org["id"], by_name["Cash and cash equivalents"],
              by_name["Share capital"], 10000, "Owner capital")
    # 2) Borrowing: Cash Dr 3000, Trade payables Cr 3000
    _post_txn(client, org["id"], by_name["Cash and cash equivalents"],
              by_name["Trade and other payables"], 3000, "Bank loan")

    fs = client.get(f"/reports/financial-position?organization_id={org['id']}")
    assert fs.status_code == 200, fs.text
    body = fs.json()
    assert body["framework"] == "IFRS"
    assert body["statement_name_en"] == "Statement of Financial Position"
    assert body["statement_name_fr"] == "Bilan"
    assert body["balanced"] is True
    assert float(body["assets"]) == float(body["liabilities"]) + float(body["equity"])
    assert float(body["assets"]) == 13000.0


def test_ohada_income_statement_separates_hao(client):
    """Ordinary result = class-7 revenue - class-6 expenses; a class-8 (HAO)
    entry appears in a SEPARATE result section, NOT blended into ordinary
    result. net_result adds the HAO net contribution back."""
    _register(client)
    org = _create_org(client, framework="OHADA")
    acc = _accounts_by_code(client, org["id"])

    # Capital base so the ledger stays balanced (cash 5711, capital 10).
    _post_txn(client, org["id"], acc["5711"], acc["10"], 15000, "Capital")

    # Ordinary revenue: Sales(70) Cr 2000, Cash(5711) Dr 2000
    _post_txn(client, org["id"], acc["5711"], acc["70"], 2000, "Cash sale")
    # Ordinary expense: Purchases(6011) Dr 500, Cash(5711) Cr 500
    _post_txn(client, org["id"], acc["6011"], acc["5711"], 500, "Stock purchase")
    # HAO revenue: Income outside ordinary(84) Cr 1000, Cash(5711) Dr 1000
    _post_txn(client, org["id"], acc["5711"], acc["84"], 1000, "Asset disposal gain")
    # HAO expense: Expenses outside ordinary(83) Dr 200, Cash(5711) Cr 200
    _post_txn(client, org["id"], acc["83"], acc["5711"], 200, "Loss on disposal")

    isrep = client.get(f"/reports/income-statement?organization_id={org['id']}")
    assert isrep.status_code == 200, isrep.text
    b = isrep.json()
    assert b["framework"] == "OHADA"
    # OHADA: LEGAL document names — identical in BOTH UI languages. Never
    # translated.
    assert b["statement_name_en"] == "Compte de résultat (OHADA)"
    assert b["statement_name_fr"] == "Compte de résultat (OHADA)"
    assert b["statement_name_en"] == b["statement_name_fr"]

    # Ordinary: 2000 revenue - 500 expense = 1500
    assert float(b["revenue_total"]) == 2000.0
    assert float(b["expense_total"]) == 500.0
    assert float(b["ordinary_result"]) == 1500.0
    # HAO (class 8) separated, not blended into ordinary:
    assert float(b["extraordinary_total"]) == 1200.0  # 1000 + 200 magnitudes
    assert float(b["net_result"]) == 2300.0  # 1500 + (1000 - 200)
    assert float(b["net_result"]) != float(b["ordinary_result"])  # separation

    # A dedicated extraordinary section exists with the two class-8 lines.
    extra = next(s for s in b["sections"] if s["key"] == "extraordinary")
    codes = sorted(l["code"] for l in extra["lines"])
    assert codes == ["83", "84"]
    # Ordinary revenue/expense sections must NOT contain class-8 accounts.
    for s in b["sections"]:
        if s["key"] in ("revenue", "expenses"):
            assert all(l["code"] not in ("83", "84") for l in s["lines"])


def test_reversed_pair_nets_to_zero_and_drafts_excluded(client):
    """A posted transaction + its reversal BOTH contribute (net to zero) on
    both statements; a separate DRAFT transaction is never counted."""
    _register(client)
    org = _create_org(client, framework="OHADA")
    acc = _accounts_by_code(client, org["id"])

    # 1) Capital base (posted): Cash(5711) Dr 10000, Capital(10) Cr 10000
    _post_txn(client, org["id"], acc["5711"], acc["10"], 10000, "Capital")
    # 2) Expense (posted): Purchases(6011) Dr 1000, Cash(5711) Cr 1000
    expense_txn = _post_txn(client, org["id"], acc["6011"], acc["5711"], 1000, "Purchase")
    # 3) Reverse the expense -> mirror cancels it (both posted/reversed count)
    _reverse(client, org["id"], expense_txn["id"])
    # 4) DRAFT (never posted): Taxes(64) Dr 500, Cash(5711) Cr 500
    draft = client.post(
        "/transactions",
        json={
            "organization_id": org["id"],
            "description": "Draft tax accrual (unposted)",
            "lines": [
                {"account_id": acc["64"]["id"], "debit": 500, "credit": 0},
                {"account_id": acc["5711"]["id"], "debit": 0, "credit": 500},
            ],
        },
    )
    assert draft.status_code in (200, 201), draft.text

    # Income statement: every IS account nets to zero (reversed pair
    # canceled, draft excluded) -> totals are zero.
    isrep = client.get(f"/reports/income-statement?organization_id={org['id']}")
    assert isrep.status_code == 200, isrep.text
    ib = isrep.json()
    assert float(ib["revenue_total"]) == 0.0
    assert float(ib["expense_total"]) == 0.0
    assert float(ib["ordinary_result"]) == 0.0
    assert float(ib["net_result"]) == 0.0
    is_names = [l["name_en"] for s in ib["sections"] for l in s["lines"]]
    assert "Purchases of goods - local" not in is_names  # reversed -> net zero
    assert "Taxes and duties" not in is_names            # draft excluded

    # Financial position: assets == liabilities + equity holds, Cash(5711) is
    # back to 10000 (reversal canceled, not double-counted), and the draft-only
    # account (64) never appears on the balance sheet.
    fs = client.get(f"/reports/financial-position?organization_id={org['id']}")
    assert fs.status_code == 200, fs.text
    fb = fs.json()
    assert fb["balanced"] is True
    assert float(fb["assets"]) == float(fb["liabilities"]) + float(fb["equity"])
    assert float(fb["assets"]) == 10000.0  # cash returned to its posted level
    all_names = [l["name_en"] for s in fb["sections"] for l in s["lines"]]
    assert "Taxes and duties" not in all_names  # draft excluded from FS too


def test_position_reconciles_with_wrong_side_account_balance(client):
    """Regression (Session 10 hotfix for the "Unbalanced" warning): an asset
    account left with a NET CREDIT balance (e.g. an overdrawn cash account)
    must still reconcile on the Financial Position statement. The raw ledger
    is perfectly balanced (every transaction is double-entry); the old
    abs() flip in _build_financial_position double-counted the wrong-side
    balance and broke assets = liabilities + equity + net_result."""
    _register(client)
    org = _create_org(client, framework="OHADA")
    acc = _accounts_by_code(client, org["id"])

    # 1) Owner capital: Cash(5711) Dr 1000, Capital(10) Cr 1000
    _post_txn(client, org["id"], acc["5711"], acc["10"], 1000, "Capital")
    # 2) Overdraft the cash account: Purchases(6011) Dr 1500, Cash(5711) Cr 1500
    _post_txn(client, org["id"], acc["6011"], acc["5711"], 1500, "Overdraft purchase")

    inc = client.get(f"/reports/income-statement?organization_id={org['id']}")
    pos = client.get(f"/reports/financial-position?organization_id={org['id']}")
    assert inc.status_code == 200, inc.text
    assert pos.status_code == 200, pos.text

    ib = inc.json()
    fb = pos.json()
    a = Decimal(fb["assets"])
    l = Decimal(fb["liabilities"])
    e = Decimal(fb["equity"])
    net = Decimal(ib["net_result"])
    # The identity MUST hold for a balanced ledger: with the old abs() flip
    # cash became +500 (instead of -500) and the statement would not reconcile.
    assert a == l + e + net
    # The overdrawn cash account shows as a NEGATIVE asset (signed position),
    # never a flipped positive magnitude.
    assert a == Decimal("-500.00")