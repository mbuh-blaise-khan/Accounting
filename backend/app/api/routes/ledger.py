"""General Ledger read endpoint (Session 8). Protected and org-scoped.

A read-only derivation over POSTED journal lines: opening balance, debit and
credit movements, running and closing balance for one account and period.
"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.ledger import LedgerOut
from app.services import ledger_service

router = APIRouter(tags=["ledger"])


@router.get("/ledger/{account_id}", response_model=LedgerOut)
def get_ledger(
    account_id: int,
    organization_id: int = Query(...),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """One account's ledger over [from, to]: opening balance, movements,
    running balance per line, closing balance — all derived from posted lines."""
    return ledger_service.get_ledger(
        db,
        current_user,
        org_id=organization_id,
        account_id=account_id,
        date_from=date_from,
        date_to=date_to,
    )