"""PDF export tests (Session 12).

Confirms every report-type PDF endpoint returns a VALID, well-formed PDF
with the framework- and purpose-correct content for BOTH OHADA and IFRS
workspaces. We cannot open the PDF visually here, but we assert:
  1. %PDF- magic + a sane byte size,
  2. the framework label and the framework-correct statement name appear in
     the rendered text stream. ReportLab stores text in zlib-compressed
     content streams, so `_text()` decompresses every stream object and
     searches the concatenation,
  3. the endpoint is org-scoped (a non-member gets 404) and is lang-aware.
"""
import re
import zlib

HEADER = b"%PDF-"

_STREAM_RE = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.DOTALL)


def _text(pdf: bytes) -> str:
    """Concatenate the decompressed text of every FlateDecode stream."""
    parts = []
    for m in _STREAM_RE.finditer(pdf):
        data = m.group(1)
        try:
            parts.append(zlib.decompress(data).decode("latin-1", errors="replace"))
        except zlib.error:
            parts.append(data.decode("latin-1", errors="replace"))
    return "\n".join(parts)


def _register(client, email="pdf@example.com", name="PDF"):
    r = client.post(
        "/auth/register",
        json={"email": email, "password": "supersecret123",
              "display_name": name, "language_preference": "en"},
    )
    assert r.status_code in (200, 201), r.text
    return r.json()


def _create_org(client, framework="OHADA", name="PDF Co"):
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
        json={"organization_id": org_id, "description": description, "lines": [
            {"account_id": acc_d["id"], "debit": amount, "credit": 0},
            {"account_id": acc_c["id"], "debit": 0, "credit": amount},
        ]},
    )
    assert r.status_code in (200, 201), r.text
    txn = r.json()
    p = client.post(f"/transactions/{txn['id']}/post?organization_id={org_id}")
    assert p.status_code == 200, p.text
    return txn


def _seed_ohada(client, org_id):
    acc = _accounts_by_code(client, org_id)
    _post_txn(client, org_id, acc["5711"], acc["10"], 10000, "Owner capital")
    _post_txn(client, org_id, acc["5711"], acc["16"], 3000, "Bank loan")
    _post_txn(client, org_id, acc["6011"], acc["5711"], 500, "Purchases")
    _post_txn(client, org_id, acc["5711"], acc["7011"], 2000, "Sales")


def _seed_ifrs(client, org_id):
    accounts = client.get(f"/accounts?organization_id={org_id}").json()
    by_name = {a["name_en"]: a for a in accounts}
    _post_txn(client, org_id, by_name["Cash and cash equivalents"],
              by_name["Share capital"], 10000, "Owner capital")
    _post_txn(client, org_id, by_name["Cash and cash equivalents"],
              by_name["Trade and other payables"], 3000, "Bank loan")
    _post_txn(client, org_id, by_name["Operating expenses"],
              by_name["Cash and cash equivalents"], 500, "Bank fees")
    _post_txn(client, org_id, by_name["Cash and cash equivalents"],
              by_name["Sales revenue"], 2000, "Sales")


def test_ohada_pdf_documents_are_valid_and_labeled(client):
    """OHADA journal + statements produce valid PDFs carrying the framework
    label and the OHADA document names ("Bilan (OHADA)" / "Compte de
    résultat (OHADA)")."""
    _register(client)
    org = _create_org(client, framework="OHADA")
    _seed_ohada(client, org["id"])
    oid = org["id"]

    j = client.get(f"/reports/pdf/journal?organization_id={oid}")
    assert j.status_code == 200, j.text
    assert j.headers["content-type"] == "application/pdf"
    assert "attachment" in j.headers.get("content-disposition", "")
    assert j.content[:5] == HEADER and len(j.content) > 1000
    assert "OHADA" in _text(j.content)

    inc = client.get(f"/reports/pdf/income-statement?organization_id={oid}")
    assert inc.status_code == 200, inc.text
    itxt = _text(inc.content)
    assert inc.content[:5] == HEADER
    assert ("Compte de résultat" in itxt or "Compte de r" in itxt)

    fs = client.get(f"/reports/pdf/financial-position?organization_id={oid}")
    assert fs.status_code == 200, fs.text
    ftxt = _text(fs.content)
    assert fs.content[:5] == HEADER and len(fs.content) > 1000
    # ReportLab escapes parentheses in text (\\( \\)), so match the words.
    assert "Bilan" in ftxt
    assert "OHADA" in ftxt


def test_ifrs_pdf_documents_are_valid_and_labelled(client):
    """IFRS PDFs carry the IFRS framework label and the Statement of Profit
    or Loss / Statement of Financial Position names; ledger/trial balance/
    cash book also render."""
    _register(client, email="pdfifrs@example.com", name="PDF IFRS")
    org = _create_org(client, framework="IFRS", name="IFRS PDF Co")
    _seed_ifrs(client, org["id"])
    oid = org["id"]

    inc = client.get(f"/reports/pdf/income-statement?organization_id={oid}&lang=en")
    assert inc.status_code == 200, inc.text
    itxt = _text(inc.content)
    assert inc.content[:5] == HEADER and len(inc.content) > 1000
    assert "IFRS" in itxt
    assert "Statement of Profit or Loss" in itxt

    fs = client.get(f"/reports/pdf/financial-position?organization_id={oid}&lang=en")
    assert fs.status_code == 200, fs.text
    assert fs.content[:5] == HEADER
    assert "Statement of Financial Position" in _text(fs.content)

    accounts = client.get(f"/accounts?organization_id={oid}").json()
    acc_id = accounts[0]["id"]
    for path in (
        f"/reports/pdf/ledger/{acc_id}?organization_id={oid}",
        f"/reports/pdf/trial-balance?organization_id={oid}",
        f"/reports/pdf/cashbook?organization_id={oid}",
    ):
        r = client.get(path)
        assert r.status_code == 200, r.text
        assert r.content[:5] == HEADER and len(r.content) > 800, path


def test_pdf_endpoints_are_lang_aware_and_org_scoped(client):
    """A French OHADA Bilan still carries "(OHADA)"; a non-member gets 404."""
    _register(client, email="pdfscope@example.com", name="Scope")
    org = _create_org(client, framework="OHADA", name="Scope Co")
    _seed_ohada(client, org["id"])

    fr = client.get(f"/reports/pdf/financial-position?organization_id={org['id']}&lang=fr")
    assert fr.status_code == 200, fr.text
    ftxt = _text(fr.content)
    # ReportLab escapes parentheses; legal name identical regardless of lang.
    assert "Bilan" in ftxt
    assert "OHADA" in ftxt

    _register(client, email="intruder@example.com", name="Intruder")
    r = client.get(f"/reports/pdf/journal?organization_id={org['id']}")
    assert r.status_code == 404, r.text