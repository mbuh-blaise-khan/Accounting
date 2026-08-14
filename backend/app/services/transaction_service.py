"""Transaction entry service.

Responsible for creating draft transactions (validating line structure and
that lines reference valid, active accounts in the org) and for listing.
Posting/balance verification and reversal live in `posting_service` (kept
separate per .clinerules).
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.account import Account
from app.models.enums import TransactionStatus
from app.models.organization import Organization, OrganizationMember
from app.models.transaction import Transaction, TransactionLine
from app.models.user import User
from app.schemas.transaction import TransactionLineOut, TransactionOut

_TRANSACTION_LOAD = joinedload(Transaction.lines).joinedload(TransactionLine.account)


def _ensure_org_access(db: Session, user: User, org_id: int) -> Organization:
    """Return the org if the user is a member; raise 404 otherwise."""
    org = db.get(Organization, org_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.org_id == org.id,
            OrganizationMember.user_id == user.id,
        )
        .first()
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return org


def create_draft_transaction(
    db: Session,
    user: User,
    organization_id: int,
    description: str,
    lines: list[dict],
) -> Transaction:
    """Create a draft transaction (no balance requirement yet)."""
    org = _ensure_org_access(db, user, organization_id)

    if not description or not description.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A plain-language description is required",
        )
    if len(lines) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A transaction must have at least two lines",
        )

    line_objects: list[TransactionLine] = []
    for item in lines:
        debit = item.get("debit") or 0
        credit = item.get("credit") or 0
        if debit < 0 or credit < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Line amounts must be non-negative",
            )
        if (debit > 0) == (credit > 0):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Each line must be a debit OR a credit, not both or neither",
            )

        account = db.get(Account, item["account_id"])
        if account is None or account.organization_id != org.id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Account {item.get('account_id')} does not exist in this organization",
            )
        if not account.active:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Account {account.code} ({account.name_en}) is inactive",
            )
        line_objects.append(
            TransactionLine(
                account_id=account.id,
                debit_amount=debit,
                credit_amount=credit,
            )
        )

    txn = Transaction(
        organization_id=org.id,
        description=description.strip(),
        status=TransactionStatus.draft,
        created_by=user.id,
    )
    for line in line_objects:
        txn.lines.append(line)
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def _get_transaction(db: Session, user: User, org_id: int, transaction_id: int) -> Transaction:
    """Fetch a transaction belonging to an org the user is a member of."""
    _ensure_org_access(db, user, org_id)
    txn = (
        db.query(Transaction)
        .options(_TRANSACTION_LOAD)
        .filter(
            Transaction.id == transaction_id,
            Transaction.organization_id == org_id,
        )
        .first()
    )
    if txn is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return txn


def get_transaction(db: Session, user: User, org_id: int, transaction_id: int) -> Transaction:
    return _get_transaction(db, user, org_id, transaction_id)


def list_transactions(db: Session, user: User, org_id: int) -> list[Transaction]:
    """Transactions for an org the user belongs to, newest first."""
    _ensure_org_access(db, user, org_id)
    return (
        db.query(Transaction)
        .options(_TRANSACTION_LOAD)
        .filter(Transaction.organization_id == org_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )


def assert_editable(transaction: Transaction) -> None:
    """Guarantee immutability: posted/reversed transactions cannot be changed.

    Use this guard in any future edit/delete path. No edit/delete endpoint
    exists in Session 6 by design — corrections happen via reversal only.
    """
    if transaction.status != TransactionStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Posted or reversed transactions are immutable — correct them "
            "with a reversing entry, not by editing or deleting",
        )


def serialize_transaction(txn: Transaction) -> TransactionOut:
    """Build the API representation, denormalizing account display fields."""
    lines_out: list[TransactionLineOut] = []
    for line in txn.lines:
        acct = line.account
        lines_out.append(
            TransactionLineOut(
                id=line.id,
                account_id=line.account_id,
                debit_amount=line.debit_amount,
                credit_amount=line.credit_amount,
                account_code=acct.code if acct else None,
                account_name_en=acct.name_en if acct else None,
                account_name_fr=acct.name_fr if acct else None,
            )
        )
    return TransactionOut(
        id=txn.id,
        organization_id=txn.organization_id,
        description=txn.description,
        status=str(txn.status.value),
        posted_at=txn.posted_at,
        created_at=txn.created_at,
        lines=lines_out,
    )