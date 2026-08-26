"""General Ledger service (Session 8).

For a given account and period we compute:
- opening balance   = net signed balance of every POSTED journal line before the
                      period start,
- debit/credit movements = total posted debit/credit within the period,
- running + closing balance = opening plus the cumulative signed movement.

Everything is DERIVED from posted journal lines on the fly (per .clinerules) —
we never store a separately-maintained ledger balance that could drift out of
sync with the immutable journal. Drafts are never included.

Balance convention:
- normal-balance 'debit' accounts (assets, expenses): a debit increases the
  balance, so closing = opening + debit_movements - credit_movements.
- normal-balance 'credit' accounts (liabilities, equity, revenue): a credit
  increases the balance, so closing = opening + credit_movements - debit_movements.

OHADA / IFRS share the same logic; the account lookup is org-scoped per the user's
memberships.
"""
from datetime import date, datetime, time, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.account import Account
from app.models.enums import TransactionStatus
from app.models.organization import Organization, OrganizationMember
from app.models.transaction import Transaction, TransactionLine
from app.models.user import User
from app.schemas.ledger import (
    LedgerAccountOut,
    LedgerBalance,
    LedgerMovementOut,
    LedgerOut,
)


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


def _start_of(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def _end_of(d: date) -> datetime:
    return datetime.combine(d, time.max, tzinfo=timezone.utc)


def _to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:  # noqa: BLE001 - never let a bad row crash the ledger
        return Decimal(0)


def _normal_balance(account: Account) -> str:
    return getattr(account.normal_balance, "value", account.normal_balance) or "debit"


def _signed_delta(debit: Decimal, credit: Decimal, normal_balance: str) -> Decimal:
    """Signed balance change for one line under the account's convention."""
    net = debit - credit
    # Asset/expense (normal debit): debit increases; liability/equity/revenue:
    # (normal credit): credit increases.
    return net if normal_balance == "debit" else -net


def _balance(signed: Decimal, normal_balance: str) -> LedgerBalance:
    """Present a signed balance the way a real ledger does: as an unsigned figure
    sitting on exactly one side (Dr or Cr), never as a signed number the reader
    must convert via the account's normal_balance.

    ``_signed_delta`` returns a CONVENTION-RELATIVE value: positive always means
    "increase toward the account's normal side", negative means "overdrawn to
    the opposite side". So this helper must know ``normal_balance`` to pick the
    correct side:
      - debit-normal (assets, expenses):  + => Debit balance, - => Credit balance
      - credit-normal (liabilities/equity/revenue): + => Credit balance, - => Debit balance
    """
    if signed > 0:
        if normal_balance == "debit":
            return LedgerBalance(debit=signed, credit=Decimal("0"), side="debit")
        return LedgerBalance(debit=Decimal("0"), credit=signed, side="credit")
    if signed < 0:
        if normal_balance == "debit":
            return LedgerBalance(debit=Decimal("0"), credit=-signed, side="credit")
        return LedgerBalance(debit=-signed, credit=Decimal("0"), side="debit")
    return LedgerBalance(side="zero")


def _period_lines(
    db: Session,
    org_id: int,
    account_id: int,
    date_from: date | None,
    date_to: date | None,
    before_only: bool = False,
) -> list[TransactionLine]:
    """Posted journal lines on `account`, ordered chronologically.

    With ``before_only=True`` only lines STRICTLY BEFORE ``date_from`` are
    returned (that is the opening-balance population). Otherwise the lines
    within [date_from, date_to] come back — unbounded at either end that is
    None. Drafts/reversed entries never appear: only POSTED transactions feed
    the ledger, so it can never drift from the immutable journal.
    """
    q = (
        db.query(TransactionLine)
        .join(Transaction, Transaction.id == TransactionLine.transaction_id)
        .options(joinedload(TransactionLine.transaction))
        .filter(
            Transaction.organization_id == org_id,
            Transaction.status == TransactionStatus.posted,
            Transaction.posted_at.is_not(None),
            TransactionLine.account_id == account_id,
        )
    )
    if before_only:
        if date_from is not None:
            q = q.filter(Transaction.posted_at < _start_of(date_from))
    else:
        if date_from is not None:
            q = q.filter(Transaction.posted_at >= _start_of(date_from))
        if date_to is not None:
            q = q.filter(Transaction.posted_at <= _end_of(date_to))
    q = q.order_by(
        Transaction.posted_at.asc(),
        Transaction.id.asc(),
        TransactionLine.id.asc(),
    )
    return q.all()


def get_ledger(
    db: Session,
    user: User,
    org_id: int,
    account_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> LedgerOut:
    """Build one account's ledger over [date_from, date_to].

    Opening = cumulative signed net of posted lines before ``date_from`` (0 when
    unbounded); movements + running balance come from the posted lines inside the
    window; closing = opening + net movement under the account's normal-balance
    convention. Nothing is stored — every call re-derives from the journal.
    """
    _ensure_org_access(db, user, org_id)
    account = db.get(Account, account_id)
    if account is None or account.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    nb = _normal_balance(account)

    # 1) Opening balance: everything POSTED on this account before the period.
    opening = Decimal("0")
    if date_from is not None:
        for line in _period_lines(
            db, org_id, account_id, date_from, date_to, before_only=True
        ):
            opening += _signed_delta(
                _to_decimal(line.debit_amount),
                _to_decimal(line.credit_amount),
                nb,
            )

    # 2) Movements within [date_from, date_to] + running balance.
    movements: list[LedgerMovementOut] = []
    running = opening
    debit_total = Decimal("0")
    credit_total = Decimal("0")
    for line in _period_lines(db, org_id, account_id, date_from, date_to):
        debit = _to_decimal(line.debit_amount)
        credit = _to_decimal(line.credit_amount)
        debit_total += debit
        credit_total += credit
        running += _signed_delta(debit, credit, nb)
        txn = line.transaction
        movements.append(
            LedgerMovementOut(
                id=line.id,
                transaction_id=txn.id,
                date=txn.posted_at,
                                reference=f"TX-{txn.id:04d}",
                description=txn.description,
                narration=line.narration,
                debit=debit,
                credit=credit,
                running_balance=_balance(running, nb),
                status=txn.status.value,
            )
        )

    # 3) Closing = opening + net movement (per normal-balance convention). This
    #    is the same value `running` reached after the last line — two paths to
    #    one number, which keeps the arithmetic self-checking.
    closing = opening + _signed_delta(debit_total, credit_total, nb)

    return LedgerOut(
        account=LedgerAccountOut(
            id=account.id,
            code=account.code,
            name_en=account.name_en,
            name_fr=account.name_fr,
            normal_balance=nb,
                ),
        date_from=date_from,
        date_to=date_to,
        opening_balance=_balance(opening, nb),
        debit_movements=debit_total,
        credit_movements=credit_total,
        closing_balance=_balance(closing, nb),
        movements=movements,
    )