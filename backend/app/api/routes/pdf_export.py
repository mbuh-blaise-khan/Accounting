"""PDF export endpoints (Session 12) — one per report type.

Each endpoint reuses the EXACT data computation the JSON endpoints already use
(calling the same service function), then hands the payload to the matching
builder in pdf_report_builders.py to render a branded, controlled PDF. This
guarantees the PDF shows precisely what the JSON/on-screen report shows.

All routes are protected and org-scoped like their JSON counterparts; the
`lang` query parameter (en|fr) selects the document's label language.
"""

from datetime import date, datetime

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services import (
    financial_statement_service,
    journal_service,
    ledger_service,
    organization_service,
    pdf_report_builders,
    trial_balance_service,
)

router = APIRouter(prefix="/reports/pdf", tags=["pdf-export"])


def _response(pdf: bytes, filename: str) -> Response:
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'},
    )


def _org_framework(db: Session, user: User, org_id: int) -> tuple[object, bool]:
    org = organization_service.get_organization_for_user(db, user, org_id)
    return org, org.framework == "OHADA"


def _period(from_date, to_date, as_of) -> str:
    if from_date or to_date:
        f = from_date or ""
        t = to_date or ""
        return f"{f} - {t}".strip(" -") if f and t else (f or t)
    if as_of:
        return str(as_of)
    return ""

@router.get("/journal")
def pdf_journal(
    organization_id: int = Query(...),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    lang: str = Query(default="en", pattern="^(en|fr)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org, is_ohada = _org_framework(db, current_user, organization_id)
    entries = journal_service.list_journal_entries(
        db, current_user, organization_id,
        date_from=date_from, date_to=date_to,
    )
    pdf = pdf_report_builders.build_journal_pdf(
        org, entries, title="Journal",
        period=_period(date_from, date_to, None),
        lang=lang, is_ohada=is_ohada,
    )
    return _response(pdf, "journal")


@router.get("/cashbook")
def pdf_cashbook(
    organization_id: int = Query(...),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    cashbook_type: str = Query(default="double", alias="type", pattern="^(single|double)$"),
    lang: str = Query(default="en", pattern="^(en|fr)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org, is_ohada = _org_framework(db, current_user, organization_id)
    entries = journal_service.list_cash_book(
        db, current_user, organization_id,
        date_from=date_from, date_to=date_to, cashbook_type=cashbook_type,
    )
    title = "Cash Book" if lang == "en" else "Livre de caisse"
    pdf = pdf_report_builders.build_cashbook_pdf(
        org, entries, title=title,
        period=_period(date_from, date_to, None),
        cashbook_type=cashbook_type, lang=lang, is_ohada=is_ohada,
    )
    return _response(pdf, "cash-book")


@router.get("/ledger/{account_id}")
def pdf_ledger(
    account_id: int,
    organization_id: int = Query(...),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    lang: str = Query(default="en", pattern="^(en|fr)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org, is_ohada = _org_framework(db, current_user, organization_id)
    ledger = ledger_service.get_ledger(
        db, current_user, org_id=organization_id, account_id=account_id,
        date_from=date_from, date_to=date_to,
    )
    pdf = pdf_report_builders.build_ledger_pdf(
        org, ledger, period=_period(date_from, date_to, None),
        lang=lang, is_ohada=is_ohada,
    )
    return _response(pdf, f"ledger-{account_id}")
@router.get("/trial-balance")
def pdf_trial_balance(
    organization_id: int = Query(...),
    as_of: date | None = Query(default=None),
    date_from: date | None = Query(default=None, alias="from"),
    columns: int = Query(default=2),
    lang: str = Query(default="en", pattern="^(en|fr)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org, is_ohada = _org_framework(db, current_user, organization_id)
    tb = trial_balance_service.get_trial_balance(
        db, current_user, org_id=organization_id,
        date_as_of=as_of, date_from=date_from, columns=columns,
    )
    pdf = pdf_report_builders.build_trial_balance_pdf(
        org, tb, period=_period(date_from, None, as_of),
        columns6=(columns == 6), lang=lang, is_ohada=is_ohada,
    )
    return _response(pdf, "trial-balance")


@router.get("/income-statement")
def pdf_income_statement(
    organization_id: int = Query(...),
    date_from: date | None = Query(default=None, alias="from"),
    as_of: date | None = Query(default=None),
    lang: str = Query(default="en", pattern="^(en|fr)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org, is_ohada = _org_framework(db, current_user, organization_id)
    income = financial_statement_service.get_income_statement(
        db=db, user=current_user, org_id=organization_id,
        date_from=date_from, as_of=as_of,
    )
    pdf = pdf_report_builders.build_income_statement_pdf(
        org, income, period=_period(date_from, None, as_of),
        lang=lang, is_ohada=is_ohada,
    )
    return _response(pdf, "income-statement")


@router.get("/financial-position")
def pdf_financial_position(
    organization_id: int = Query(...),
    as_of: date | None = Query(default=None),
    lang: str = Query(default="en", pattern="^(en|fr)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org, is_ohada = _org_framework(db, current_user, organization_id)
    position = financial_statement_service.get_financial_position(
        db=db, user=current_user, org_id=organization_id, as_of=as_of,
    )
    pdf = pdf_report_builders.build_position_pdf(
        org, position, period=_period(None, None, as_of),
        lang=lang, is_ohada=is_ohada,
    )
    return _response(pdf, "financial-position")
