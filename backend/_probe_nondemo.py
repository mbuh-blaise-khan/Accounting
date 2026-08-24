"""Live proof of the Session 8 non-demo seeding fix (real API + real DB).

Shows:
(A) A NEW non-demo OHADA org, created through the real API, has the full
    representative SYSCOHADA chart immediately (not zero accounts).
(B) A NEW non-demo IFRS org, created through the real API, has the IAS-1
    template immediately (the same gap existed -- both were seeded only when
    is_demo=True before this fix).
(C) The autocomplete search (exact port of frontend searchAccounts) on the new
    non-demo OHADA chart: progressive digit-prefix narrowing AND name<->number
    round trips.
(D) Backfilled orgs (org 3 / org 6 / org 11) now have the chart + their posted
    transactions intact.
"""
import time
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.account import Account
from app.models.organization import Organization


def search(accts, query, byNameOnly=False):
    """Exact port of frontend searchAccounts (accountLookup.js, Session 8):
    code matching is PREFIX-based; name matching is substring (EN/FR)."""
    q = (query or "").strip().lower()
    if not q:
        return []
    def nameHit(a):
        return ((a[1] or "").lower().count(q) > 0) or ((a[2] or "").lower().count(q) > 0)
    def codeHit(a):
        return (a[0] or "").lower().startswith(q)
    key = lambda a: ((a[0] if not byNameOnly else a[1]) or "")
    rows = [a for a in accts if (nameHit(a) if byNameOnly else (nameHit(a) or codeHit(a)))]
    rows.sort(key=lambda a: key(a).lower())
    return rows


print("=== (A)+(B) NEW non-demo orgs through the real API ===")
c = TestClient(app)
email = f"nondemo_{int(time.time())}@x.local"
reg = c.post("/auth/register", json={
    "email": email, "password": "supersecret123",
    "display_name": "ND", "language_preference": "en"})
print("register:", reg.status_code, "cookie:", bool(c.cookies.get("access_token")))

# --- New NON-DEMO OHADA org ---
r = c.post("/organizations", json={
    "name": "Real OHADA Business", "framework": "OHADA", "currency": "XAF", "is_demo": False})
print("create non-demo OHADA:", r.status_code, "| is_demo:", r.json().get("is_demo"))
oh = r.json()["id"]
r = c.get("/accounts", params={"organization_id": oh})
ac = r.json()
codes = sorted(a.get("code") for a in ac if a.get("code"))
print(f"  GET /accounts -> {r.status_code} count={len(ac)}")
print("  has 5711:", any(a.get('code')=='5711' for a in ac),
      "| has 7011:", any(a.get('code')=='7011' for a in ac),
      "| has 57:", any(a.get('code')=='57' for a in ac))
print("  codes_head:", codes[:14])

# --- New: NON-DEMO IFRS org ---
r = c.post("/organizations", json={
    "name": "Real IFRS Business", "framework": "IFRS", "currency": "XAF", "is_demo": False})
print("create non-demo IFRS:", r.status_code, "| is_demo:", r.json().get("is_demo"))
ifr = r.json()["id"]
r = c.get("/accounts", params={"organization_id": ifr})
ac_f = r.json()
print(f"  GET /accounts -> count={len(ac_f)} codes_present={sum(1 for a in ac_f if a.get('code'))}")
print("  names_head:", [a.get('name_en') for a in ac_f][:4])

print("\n=== (C) searchAccounts over the NEW non-demo OHADA chart (real rows) ===")
db = SessionLocal()
ohada_rows = [(a.code, a.name_en, a.name_fr) for a in db.query(Account).filter(Account.organization_id == oh).all()]
for query in ("5", "51", "512", "57", "571", "5711", "70", "011", "cash", "caisse", "ventes"):
    matches = search(ohada_rows, query)
    print(f"  '{query}' -> {[(m[0], m[1]) for m in matches][:12]}")

# Bidirectional: name -> number, and number -> name (what the picker displays).
print("\n  name->number: search 'cash' first hit:", search(ohada_rows, 'cash')[0])
print("  number->name: search '5711' first hit:", search(ohada_rows, '5711')[0])
print("  number->name: search '701' first hit:", search(ohada_rows, '701')[0])

print("\n=== (D) Backfilled non-demo orgs + txn integrity ===")
for o in db.query(Organization).order_by(Organization.id).all():
    if o.is_demo:
        continue
    n = db.query(Account).filter(Account.organization_id == o.id).count()
    print(f"  org {o.id} {o.name!r} fw={o.framework.value} non-demo accts={n}")
# The real-business case: org 11 had posted transactions created against an
# empty chart's 2 accounts; verify those still resolve after backfill.
from sqlalchemy import text
for oid in (6, 11):
    refs = db.execute(text(
        "SELECT DISTINCT tl.account_id FROM transaction_lines tl "
        "JOIN transactions t ON t.id = tl.transaction_id WHERE t.organization_id = :oid"
    ), {"oid": oid}).fetchall()
    acct_ids = {a.id for a in db.query(Account).filter(Account.organization_id == oid).all()}
    dangling = [x[0] for x in refs if x[0] not in acct_ids]
    print(f"  org {oid}: txn-referenced accounts={len(refs)} dangling={dangling}")
db.close()
print("\nDONE")