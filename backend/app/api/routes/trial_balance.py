"""Trial Balance endpoint (Session 9). Protected and org-scoped.

GET /trial-balance?organization_id=&as_of=&from=&columns=2|4|6

`columns` selects the VIEW (default 2). The response always carries opening/
movement/closing figures so the frontend can switch views without refetching
(documented decision in schemas/trial_balance.py).
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.trial_balance import TrialBalanceOut
from app.services import trial_balance_service

router = APIRouter(tags=["trial-balance"])


@router.get("/trial-balance", response_model=TrialBalanceOut)
def get_trial_balance(
    organization_id: int = Query(...),
    as_of: date | None = Query(default=None),
    date_from: date | None = Query(default=None, alias="from"),
    columns: int = Query(default=2),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trial balance for one organization: every account's opening balance,
    period movement and closing balance (all three always present; `columns`
    tells the frontend which view to render by default)."""
    if columns not in (2, 4, 6):
        raise HTTPException(status_code=422, detail="columns must be 2, 4 or 6")
    return trial_balance_service.get_trial_balance(
        db,
        current_user,
        org_id=organization_id,
        date_as_of=as_of,
        date_from=date_from,
        columns=columns,
    )
