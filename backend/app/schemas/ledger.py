"""Pydantic schemas for the General Ledger (Session 8)."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class LedgerAccountOut(BaseModel):
    """Identity + balance convention for the account the ledger is about."""

    id: int
    code: Optional[str] = None
    name_en: str
    name_fr: str
    normal_balance: str  # 'debit' | 'credit'


class LedgerMovementOut(BaseModel):
    """One posted journal line on the account, with its running (post-period)
    balance. The date is the transaction's real `posted_at` (Part C)."""

    id: int  # transaction_line.id (drill-down key)
    transaction_id: int
    date: Optional[datetime] = None  # posted_at
    reference: str
    description: str
    narration: Optional[str] = None
    debit: Decimal
    credit: Decimal
    running_balance: Decimal
    status: str = "posted"


class LedgerOut(BaseModel):
    """A single account's ledger over [date_from, date_to].

    All balances are DERIVED from posted journal lines (opening = cumulative net
    before `date_from`; movements + running within the window) — nothing stored.
    `date_from`/`date_to` are the inclusive period bounds (None = unbounded).
    """

    account: LedgerAccountOut
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    opening_balance: Decimal
    debit_movements: Decimal
    credit_movements: Decimal
    closing_balance: Decimal
    movements: list[LedgerMovementOut] = []