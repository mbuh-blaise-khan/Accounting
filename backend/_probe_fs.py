"""URGENT root-cause probe (Session 10 balance-reconciliation report).

Pass 1: raw ledger balance per org (sum of posted+reversed lines' debits vs credits).
Pass 2: reproduce the Financial Position + Income Statement values for every org
        using the REAL service builders (no API auth involved).
Pass 3: for any org that does NOT reconcile, dump PER-ACCOUNT activity + the
        classification decision each account received, so we can see whether the
        imbalance is in the DATA or in the CLASSIFICATION.

Read-only: this script never writes.
"""
import sys, os
from decimal import Decimal

BACKEND = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.organization import Organization
from app.models.account import Account
from app.services.financial_statement_service import (
    _build_financial_position,
    _build_income_statement,
    _classify_balance_sheet_account,
    _account_sums,
)

eng = create_engine(settings.DATABASE_URL)
S = sessionmaker(bind=eng)
db = S()

print("=" * 90)
print("PASS 1 — RAW LEDGER BALANCE PER ORG (posted + reversed lines only)")
print("=" * 90)
print()
print("=" * 90)
print("PASS 1.5 — PER-TRANSACTION BALANCE (orgs with posted/reversed activity)")
print("  Confirms no single transaction is unbalanced (two offsetting bad txns would hide)")
print("=" * 90)
per_txn = db.execute(
    text(
        """
        SELECT t.organization_id AS org_id, t.id AS txn_id, t.status,
               COALESCE(SUM(tl.debit_amount), 0)  AS d,
               COALESCE(SUM(tl.credit_amount), 0) AS c
        FROM transactions t
        JOIN transaction_lines tl ON tl.transaction_id = t.id
        WHERE t.status IN ('posted','reversed')
        GROUP BY t.organization_id, t.id, t.status
        ORDER BY t.organization_id, t.id
        """
    )
).all()
bad_txn = 0
for org_id, txn_id, status, d, c in per_txn:
    d = Decimal(d or 0)
    c = Decimal(c or 0)
    if d != c:
        bad_txn += 1
        print(f"  -> org {org_id} transaction {txn_id} [{status}] D={d} C={c}  <<< UNBALANCED TXN")
if bad_txn == 0:
    print("  ALL individual transactions are balanced (each debit == credit).")
raw = db.execute(
    text(
        """
        SELECT o.id AS org_id, o.name, o.framework,
               COALESCE(SUM(tl.debit_amount), 0)  AS total_debit,
               COALESCE(SUM(tl.credit_amount), 0) AS total_credit,
               COUNT(DISTINCT t.id) AS line_txns
        FROM organizations o
        LEFT JOIN transactions t
               ON t.organization_id = o.id AND t.status IN ('posted','reversed')
        LEFT JOIN transaction_lines tl ON tl.transaction_id = t.id
        GROUP BY o.id, o.name, o.framework
        ORDER BY o.id
        """
    )
).all()

orgs = db.query(Organization).order_by(Organization.id).all()
org_by_id = {o.id: o for o in orgs}
matched = []
for r in raw:
    org_id, name, fw, d, c, n = r
    d = Decimal(d or 0)
    c = Decimal(c or 0)
    balanced = d == c
    print(f"org {org_id} [{fw}] '{name}': txn_count={n}  RAW debit={d}  RAW credit={c}  RAW_BALANCED={balanced}")
    if not balanced:
        matched.append(org_id)

print()
print("=" * 90)
print("PASS 2 — STATEMENT VIEW PER ORG (via the REAL service builders)")
print("  A / L / E from _build_financial_position; net_result from _build_income_statement")
print("  reconciles? -> assets == liabilities + equity + net_result")
print("=" * 90)
problems = []
for org in orgs:
    try:
        pos = _build_financial_position(db, org, None)
        inc = _build_income_statement(db, org, None, None)
    except Exception as e:  # noqa: BLE001 - report don't crash
        print(f"org {org.id} [{org.framework}] ERROR building statement: {e!r}")
        continue
    a = Decimal(pos.assets)
    l = Decimal(pos.liabilities)
    e = Decimal(pos.equity)
    r = Decimal(inc.net_result)
    ok = (a == l + e + r)
    flag = "" if ok else "   <-- DOES NOT RECONCILE"
    print(
        f"org {org.id} [{org.framework}] A={a} L={l} E={e} net_result={r} "
        f"(A==L+E+R:{ok}){flag}"
    )
    if not ok:
        problems.append(org.id)

print()
print("=" * 90)
print("PASS 3 — DEEP DIVE for orgs that do NOT reconcile")
print("=" * 90)
for org_id in problems:
    org = org_by_id[org_id]
    ohada = getattr(org.framework, "value", org.framework) == "OHADA"
    sums = _account_sums(db, org.id, None, None)
    print(f"\n--- org {org_id} [{org.framework}] ---")
    accounts = db.query(Account).filter(Account.organization_id == org.id).all()
    for acct in sorted(accounts, key=lambda a: (a.code is None, a.code or "", a.name_en)):
        d, c = sums.get(acct.id, (Decimal("0"), Decimal("0")))
        if d == 0 and c == 0:
            continue
        kind = _classify_balance_sheet_account(acct, ohada)
        cls = getattr(acct, "ohada_class_number", None)
        limit = "none" if ohada and (cls is None or cls in (8, 9)) else ""
        limit = "skipped-OHADA" if (ohada and cls is None) else limit
        acct_class = getattr(acct, "account_class", None)
        acct_class = getattr(acct_class, "value", acct_class)
        print(
            f"  acct {acct.id} code={acct.code!r} name='{acct.name_en}' "
            f"class={acct_class!r} ohada_cls={cls} "
            f"D={d} C={c} net_signed={d - c} -> balance_kind={kind!r} {limit}"
        )

print()
print("=" * 90)
print("DONE")
print("=" * 90)
db.close()