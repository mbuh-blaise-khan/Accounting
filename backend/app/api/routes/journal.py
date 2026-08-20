"""Journal and Cash Book read endpoints (Session 7). All routes are protected
and org-scoped. They are read-only views over POSTED transactions."""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.journal import JournalEntryOut
from app.services import journal_service

router = APIRouter(tags=["journal"])


@router.get("/journal-entries", response_model=list[JournalEntryOut])
def list_journal_entries(
    organization_id: int = Query(...),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    account_id: int | None = Query(default=None),
    reference: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Posted transaction lines for an org's Journal (filterable by date
    range, account and reference)."""
    return journal_service.list_journal_entries(
        db, current_user, organization_id,
        date_from=date_from, date_to=date_to,
        account_id=account_id, reference=reference,
    )


@router.get("/cashbook", response_model=list[JournalEntryOut])
def list_cash_book(
    organization_id: int = Query(...),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    account_id: int | None = Query(default=None),
    reference: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cash Book: posted lines on cash/bank accounts only (same filters)."""
    return journal_service.list_cash_book(
        db, current_user, organization_id,
        date_from=date_from, date_to=date_to,
        account_id=account_id, reference=reference,
    )