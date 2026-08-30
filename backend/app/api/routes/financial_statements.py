"""Financial-statement endpoints (Session 10, Part A).

GET /reports/income-statement?organization_id=&period=&as_of=
    -> OHADA "Compte de résultat" / IFRS "Statement of Profit or Loss"

GET /reports/financial-position?organization_id=&as_of=
    -> OHADA "Bilan" / IFRS "Statement of Financial Position"

All figures are DERIVED from posted journal lines (never manually entered).
Reversed transactions + their originals both contribute (net to zero);
drafts are excluded. Statements are read-only views of the ledger.
"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.financial_statement import FinancialPositionOut, IncomeStatementOut
from app.services import financial_statement_service

router = APIRouter(prefix="/reports", tags=["financial-statements"])


@router.get("/income-statement", response_model=IncomeStatementOut)
def get_income_statement(
    organization_id: int = Query(...),
    date_from: date | None = Query(default=None, alias="from"),
    as_of: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Income statement for one organization over [from, as_of] (None = open-ended).

    Returns framework-correct labels: OHADA -> "Compte de résultat",
    IFRS -> "Statement of Profit or Loss". Ordinary revenue minus ordinary
    expenses, plus a separate HAO (class-8) section for OHADA.
    """
    return financial_statement_service.get_income_statement(
        db=db, user=current_user, org_id=organization_id, date_from=date_from, as_of=as_of
    )


@router.get("/financial-position", response_model=FinancialPositionOut)
def get_financial_position(
    organization_id: int = Query(...),
    as_of: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Statement of financial position (Bilan / IFRS SFP) as of `as_of`.

    Uses closing balances. Returns framework-correct labels: OHADA ->
    "Bilan", IFRS -> "Statement of Financial Position".
    """
    return financial_statement_service.get_financial_position(
        db=db, user=current_user, org_id=organization_id, as_of=as_of
    )
