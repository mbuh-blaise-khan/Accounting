"""Per-report PDF builders (Session 12).

Turns each report's already-computed payload (the same schema the JSON
endpoints return) into the generic spec consumed by
pdf_export_service.build_report_pdf(), keeping routes thin and each builder
unit-testable. Labels come from the payloads (framework- and purpose-correct
statement names) and the bilingual label map in pdf_export_service.
"""
from datetime import datetime

from app.models.organization import Organization
from app.schemas.financial_statement import (
    FinancialPositionOut,
    IncomeStatementOut,
)
from app.schemas.journal import JournalEntryOut
from app.schemas.ledger import LedgerOut
from app.schemas.trial_balance import TrialBalanceOut
from app.services.pdf_export_service import _LABELS, build_report_pdf


def _fw_label(fw: str) -> str:
    return "OHADA" if fw == "OHADA" else "IFRS"


def _identity_rows(org: Organization, *, framework: str, period: str,
                   address: str, lang: str) -> list[tuple[str, str]]:
    l = _LABELS[lang]
    rows = [(l["framework"], framework), (l["period"], period)]
    if address:
        rows.append((l["address"], address))
    if org.rccm_number:
        rows.append((l["rccm"], org.rccm_number))
    if org.tax_id:
        rows.append((l["tax_id"], org.tax_id))
    return rows


def build_journal_pdf(org, entries, *, title, period, lang="en",
                      is_ohada=False, generated_at=None):
    l = _LABELS[lang]
    columns = [
        (l["date"], "left"), (l["reference"], "center"), (l["description"], "left"),
    ] + ([(l["account_no"], "left")] if is_ohada else []) + [
        (l["account"], "left"), (l["debit"], "right"), (l["credit"], "right"),
    ]
    rows = []
    for e in entries:
        acct = (e.account_name_fr if lang == "fr" and e.account_name_fr
                else e.account_name_en or "")
        left = [
            e.date.strftime("%d/%m/%Y") if e.date else "", e.reference or "",
            e.description or "",
        ]
        if is_ohada:
            left.append(e.account_code or "")
        rows.append(("data", left + [acct,
                                     str(e.debit) if e.debit else "",
                                     str(e.credit) if e.credit else ""]))
    identity = _identity_rows(org, framework=_fw_label(org.framework),
                              period=period, address=org.registered_address or "", lang=lang)
    return build_report_pdf(org_name=org.name, title=title, period=period,
                            footer_rows=identity, columns=columns, rows=rows,
                            lang=lang, generated_at=generated_at)


def build_cashbook_pdf(org, entries, *, title, period, cashbook_type="double",
                       lang="en", is_ohada=False, generated_at=None):
    l = _LABELS[lang]
    base = [
        (l["date"], "left"), (l["reference"], "center"), (l["description"], "left"),
    ] + ([(l["account_no"], "left")] if is_ohada else [])
    if cashbook_type == "double":
        columns = base + [
            (l["cash_debit"], "right"), (l["bank_debit"], "right"),
            (l["cash_credit"], "right"), (l["bank_credit"], "right"),
        ]
    else:
        columns = base + [(l["debit"], "right"), (l["credit"], "right")]
    rows = []
    for e in entries:
        cb = getattr(e, "cashbook_type", None) or "cash"
        if cashbook_type == "double":
            cells = [
                str(e.debit) if cb == "cash" else "", str(e.debit) if cb == "bank" else "",
                str(e.credit) if cb == "cash" else "", str(e.credit) if cb == "bank" else "",
            ]
        else:
            cells = [str(e.debit), str(e.credit)]
        left = [
            e.date.strftime("%d/%m/%Y") if e.date else "", e.reference or "",
            e.description or "",
        ]
        if is_ohada:
            left.append(e.account_code or "")
        rows.append(("data", left + cells))
    identity = _identity_rows(org, framework=_fw_label(org.framework),
                              period=period, address=org.registered_address or "", lang=lang)
    return build_report_pdf(org_name=org.name, title=title, period=period,
                            footer_rows=identity, columns=columns, rows=rows,
                            lang=lang, generated_at=generated_at)


def build_ledger_pdf(org, ledger, *, period, lang="en", is_ohada=False,
                     generated_at=None):
    l = _LABELS[lang]
    title = (f"{ledger.account.code} · " if ledger.account.code else "") + (
        ledger.account.name_fr if lang == "fr" else ledger.account.name_en
    )
    columns = [
        (l["date"], "left"), (l["reference"], "center"), (l["description"], "left"),
        (l["debit"], "right"), (l["credit"], "right"), (l["balance"], "right"),
    ]
    rows = []
    opening = ledger.opening_balance
    rows.append(("total", [l["opening"], "", "",
                           str(opening.debit) if opening.side == "debit" else "",
                           str(opening.credit) if opening.side == "credit" else "",
                           str(opening.debit or opening.credit)]))
    for m in ledger.movements:
        rb = m.running_balance
        bal = rb.debit if rb.side == "debit" else rb.credit if rb.side == "credit" else "0"
        rows.append(("data", [
            m.date.strftime("%d/%m/%Y") if m.date else "", m.reference or "",
            m.description or "", str(m.debit), str(m.credit), str(bal),
        ]))
    closing = ledger.closing_balance
    rows.append(("total", [l["closing"], "", "",
                           str(closing.debit) if closing.side == "debit" else "",
                           str(closing.credit) if closing.side == "credit" else "",
                           str(closing.debit or closing.credit)]))
    identity = _identity_rows(org, framework=_fw_label(org.framework),
                              period=period, address=org.registered_address or "", lang=lang)
    return build_report_pdf(org_name=org.name, title=title, period=period,
                            footer_rows=identity, columns=columns, rows=rows,
                            lang=lang, generated_at=generated_at)


def build_trial_balance_pdf(org, tb, *, period, columns6=False, lang="en",
                            is_ohada=False, generated_at=None):
    l = _LABELS[lang]
    rows = []
    if columns6:
        columns = [
            (l["account"], "left"), (l["opening"], "right"),
            (l["movement"], "right"), (l["closing"], "right"),
        ]
        for r in tb.rows:
            nm = (f"{r.code} · " if r.code else "") + (r.name_fr if lang == "fr" else r.name_en)
            rows.append(("data", [nm, str(r.opening_debit), str(r.movement_debit), str(r.closing_debit)]))
            rows.append(("data", ["", str(r.opening_credit), str(r.movement_credit), str(r.closing_credit)]))
        rows.append(("total", [l["total"], str(tb.totals.opening_debit),
                               str(tb.totals.movement_debit), str(tb.totals.closing_debit)]))
    else:
        columns = [
            (l["account"], "left"), (l["opening"], "right"),
            (l["movement"], "right"), (l["closing"], "right"),
        ]
        for r in tb.rows:
            nm = (f"{r.code} · " if r.code else "") + (r.name_fr if lang == "fr" else r.name_en)
            op = r.opening_debit if r.opening_debit else r.opening_credit
            mv = r.movement_debit if r.movement_debit else r.movement_credit
            cl = r.closing_debit if r.closing_debit else r.closing_credit
            rows.append(("data", [nm, str(op), str(mv), str(cl)]))
        rows.append(("total", [l["total"],
                               str(tb.totals.opening_debit or tb.totals.opening_credit),
                               str(tb.totals.movement_debit or tb.totals.movement_credit),
                               str(tb.totals.closing_debit or tb.totals.closing_credit)]))
    ttitle = "Balance de vérification" if lang == "fr" else "Trial Balance"
    identity = _identity_rows(org, framework=_fw_label(org.framework),
                              period=period, address=org.registered_address or "", lang=lang)
    return build_report_pdf(org_name=org.name, title=ttitle, period=period,
                            footer_rows=identity, columns=columns, rows=rows,
                            lang=lang, generated_at=generated_at)
def _statement_name(income, lang):
    return income.statement_name_fr if lang == "fr" else income.statement_name_en


def build_income_statement_pdf(org, income, *, period, lang="en",
                               is_ohada=False, generated_at=None):
    """Renders the Income Statement / Compte de résultat, keeping the
    ordinary vs HAO (class-8) split as SEPARATE sections exactly as the JSON
    payload structure does (never merged)."""
    l = _LABELS[lang]
    name = (income.statement_name_fr if lang == "fr"
            else income.statement_name_en)
    # Columns: [code col for OHADA] account + amount.
    columns = [
        (l["account_no"], "left") if is_ohada else (l["account"], "left"),
        (l["account"], "left"),
        ("Amount (montant)" if lang == "en" else "Montant", "right"),
    ]
    rows = []
    for section in income.sections:
        label = section.label_fr if lang == "fr" else section.label_en
        rows.append(("section", [label]))
        for line in section.lines:
            nm = line.name_fr if lang == "fr" else line.name_en
            rows.append(("data", [
                line.code or "" if is_ohada else "", nm, str(line.amount),
            ]))
        rows.append(("total", ["", f"{label} — {l['total']}", str(section.total)]))
    rows.append(("total", ["", l["total"], str(income.net_result)]))
    identity = _identity_rows(org, framework=_fw_label(org.framework),
                              period=period, address=org.registered_address or "", lang=lang)
    return build_report_pdf(org_name=org.name, title=name, period=period,
                            footer_rows=identity, columns=columns, rows=rows,
                            lang=lang, generated_at=generated_at)


def build_position_pdf(org, position, *, period, lang="en", is_ohada=False,
                       generated_at=None):
    l = _LABELS[lang]
    name = (position.statement_name_fr if lang == "fr"
            else position.statement_name_en)
    columns = [
        (l["account_no"], "left") if is_ohada else (l["account"], "left"),
        (l["account"], "left"),
        ("Amount (montant)" if lang == "en" else "Montant", "right"),
    ]
    rows = []
    for section in position.sections:
        label = section.label_fr if lang == "fr" else section.label_en
        rows.append(("section", [label]))
        for line in section.lines:
            nm = line.name_fr if lang == "fr" else line.name_en
            rows.append(("data", [
                line.code or "" if is_ohada else "", nm, str(line.amount),
            ]))
        rows.append(("total", ["", f"{label} — {l['total']}", str(section.total)]))
    identity = _identity_rows(org, framework=_fw_label(org.framework),
                              period=period, address=org.registered_address or "", lang=lang)
    return build_report_pdf(org_name=org.name, title=name, period=period,
                            footer_rows=identity, columns=columns, rows=rows,
                            lang=lang, generated_at=generated_at)