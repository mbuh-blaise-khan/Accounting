"""Cross-check the frontend accountLookup.test.mjs assertions with an exact
Python port of searchAccounts (which cannot execute in this non-TTY shell)."""
import json

def search(accts, query, byNameOnly=False):
    q = (query or "").strip().lower()
    if not q:
        return []
    def name_hit(a):
        return q in (a["name_en"] or "").lower() or q in (a["name_fr"] or "").lower()
    def code_hit(a):
        return (a["code"] or "").lower().startswith(q)
    sort_key = lambda a: (a["name_en"] if byNameOnly else a["code"]) or ""
    rows = [a for a in accts if (name_hit(a) if byNameOnly else (name_hit(a) or code_hit(a)))]
    rows.sort(key=lambda a: str(sort_key(a)).lower())
    return rows

ok = True
def check(got, want, label):
    global ok
    if got != want:
        ok = False
        print("FAIL", label, "got", got, "want", want)

# Fixture EXACTLY as in accountLookup.test.mjs (progressive-narrowing check).
ohada = [
    {"id": 1, "code": "60", "name_en": "Purchases", "name_fr": "Achats"},
    {"id": 2, "code": "601", "name_en": "Materials", "name_fr": "Fournitures"},
    {"id": 3, "code": "6011", "name_en": "Raw materials", "name_fr": "Matieres prem"},
    {"id": 4, "code": "6012", "name_en": "Work in progress", "name_fr": "Travaux encours"},
    {"id": 5, "code": "603", "name_en": "Services purchased", "name_fr": "Prestations"},
    {"id": 6, "code": "51", "name_en": "Pooled funds", "name_fr": "Fonds de placement"},
    {"id": 7, "code": "512", "name_en": "Current bank accounts", "name_fr": "Banque (courant)"},
    {"id": 8, "code": "571", "name_en": "Cash - national currency", "name_fr": "Caisse - monnaie"},
    {"id": 9, "code": "5711", "name_en": "Cash in hand", "name_fr": "Caisse"},
    {"id": 10, "code": "5712", "name_en": "Cash in banks", "name_fr": "Banque"},
]
cd = lambda r: [a["code"] for a in r]

check(cd(search(ohada, "5")), ["51", "512", "571", "5711", "5712"], "'5' class 5")
check(cd(search(ohada, "51")), ["51", "512"], "'51'")
check(cd(search(ohada, "512")), ["512"], "'512'")
check(cd(search(ohada, "57")), ["571", "5711", "5712"], "'57'")
check(cd(search(ohada, "5711")), ["5711"], "'5711'")
check(search(ohada, "011"), [], "'011' prefix-not-substring")
check(cd(search(ohada, "571")), ["571", "5711", "5712"], "'571' subtree")
check(cd(search(ohada, "60")), ["60", "601", "6011", "6012", "603"], "'60' subtree")
check(cd(search(ohada, "caisse")), ["571", "5711"], "'caisse' name")

# byNameOnly regression
ifrs = [
    {"id": 1, "code": None, "name_en": "Cash and cash equivalents", "name_fr": "Tr\u00e9sorerie"},
    {"id": 2, "code": None, "name_en": "Sales revenue", "name_fr": "Produits des ventes"},
]
check(search(ifrs, "1", True), [], "ifrs code-shaped ignored")
# name search still resolves (code is None) on the IFRS template:
check([a["name_en"] for a in search(ifrs, "cash", True)], ["Cash and cash equivalents"], "ifrs name match")

print("ALL OK" if ok else "SOME FAILED")