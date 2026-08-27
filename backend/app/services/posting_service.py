"""Posting service — balance verification + immutability + reversal.

Separate from `transaction_service` (per .clinerules). The critical guarantee:
a transaction may only be marked posted when total debits == total credits.
This is verified HERE, in the service layer, never only in the UI — so a
client can never post an unbalanced transaction.
"""
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import TransactionStatus
from app.models.transaction import Transaction, TransactionLine
from app.services import transaction_service


def _to_decimal(value) -> Decimal:
    """Coerce an amount to Decimal safely (SQLite returns floats, PG Decimals)."""
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _balance_of(lines: list[TransactionLine]) -> tuple[Decimal, Decimal]:
    """(total_debits, total_credits) for a set of lines."""
    total_debit = sum((_to_decimal(l.debit_amount) for l in lines), Decimal(0))
    total_credit = sum((_to_decimal(l.credit_amount) for l in lines), Decimal(0))
    return total_debit, total_credit


def post_transaction(
    db: Session, user, org_id: int, transaction_id: int
) -> Transaction:
    """Validate balance and mark a draft transaction as posted (immutable)."""
    txn = transaction_service.get_transaction(db, user, org_id, transaction_id)
    if txn.status != TransactionStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft transactions can be posted",
        )

    lines = (
        db.query(TransactionLine)
        .filter(TransactionLine.transaction_id == txn.id)
        .all()
    )
    if len(lines) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A transaction must have at least two lines",
        )

    # ENFORCED AT THE SERVICE LAYER: posting an unbalanced entry is impossible.
    total_debit, total_credit = _balance_of(lines)
    if total_debit != total_credit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot post unbalanced transaction: total debits ({total_debit}) "
                f"must equal total credits ({total_credit})"
            ),
        )

    txn.status = TransactionStatus.posted
    txn.posted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(txn)
    return txn


def reverse_transaction(
    db: Session, user, org_id: int, transaction_id: int
) -> Transaction:
    """Reverse a posted transaction by creating a real, opposite journal entry.

    Posted records are immutable (never edited or deleted). Corrections happen
    exclusively via a reversing entry: this creates a NEW posted transaction
    that exactly mirrors the original with debit/credit sides swapped, posts it
    now, and links it back to the original via `reverse_of_id`. The original is
    marked `reversed` (shown as a badge) but its rows are never altered.

    Only a POSTED transaction may be reversed — drafts and already-reversed
    transactions are rejected. The mirrored entry is balanced by construction
    (swapping sides preserves total debits == total credits), so it is posted
    directly.
    """
    txn = transaction_service.get_transaction(db, user, org_id, transaction_id)
    if txn.status != TransactionStatus.posted:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only posted transactions can be reversed — drafts and "
            "already-reversed transactions are not reversible",
        )

    lines = (
        db.query(TransactionLine)
        .filter(TransactionLine.transaction_id == txn.id)
        .all()
    )
    if len(lines) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot reverse a transaction with fewer than two lines",
        )

    # Build the mirror: same accounts, sides swapped, so it balances by
    # construction and its net effect cancels the original.
    reversal = Transaction(
        organization_id=txn.organization_id,
        description=f"Reversal of {txn.description}",
        status=TransactionStatus.posted,
        posted_at=datetime.now(timezone.utc),
        created_by=user.id,
        reverse_of_id=txn.id,
    )
    for line in lines:
        reversal.lines.append(
            TransactionLine(
                account_id=line.account_id,
                debit_amount=_to_decimal(line.credit_amount),
                credit_amount=_to_decimal(line.debit_amount),
                narration=(f"Reversal of {line.narration}" if line.narration else None),
            )
        )

    # Mark the original reversed WITHOUT touching its rows. The mirror carries
    # the link back to this original.
    txn.status = TransactionStatus.reversed
    db.add(reversal)
    db.commit()
    db.refresh(reversal)
    return reversal