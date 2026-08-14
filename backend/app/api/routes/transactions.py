"""Transaction entry and posting endpoints. All routes are protected and
org-scoped. Posting an unbalanced transaction is rejected in the service layer.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionOut
from app.services import posting_service, transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a draft transaction (balance required only at posting time)."""
    txn = transaction_service.create_draft_transaction(
        db=db,
        user=current_user,
        organization_id=payload.organization_id,
        description=payload.description,
        lines=[line.model_dump() for line in payload.lines],
    )
    return transaction_service.serialize_transaction(txn)


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    organization_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List transactions for an organization the user is a member of."""
    txns = transaction_service.list_transactions(db, current_user, organization_id)
    return [transaction_service.serialize_transaction(t) for t in txns]


@router.post("/{transaction_id}/post", response_model=TransactionOut)
def post_transaction(
    transaction_id: int,
    organization_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate balance and post a draft transaction (makes it immutable)."""
    txn = posting_service.post_transaction(db, current_user, organization_id, transaction_id)
    return transaction_service.serialize_transaction(txn)


@router.post("/{transaction_id}/reverse", response_model=TransactionOut)
def reverse_transaction(
    transaction_id: int,
    organization_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reverse a posted transaction (stub — corrections detailed later)."""
    txn = posting_service.reverse_transaction(db, current_user, organization_id, transaction_id)
    return transaction_service.serialize_transaction(txn)