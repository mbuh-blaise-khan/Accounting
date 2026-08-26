"""Pydantic schemas for the General Ledger (Session 8; balance presentation
corrected post-Session-8 per standard bookkeeping convention).

Convention (researched): a ledger posts debits on the LEFT and credits on the
RIGHT, and each account's balance is shown sitting ON ONE SIDE — either a
"debit balance" or a "credit balance", labelled accordingly, never as a single
signed number the reader must interpret through the account's normal_balance.
LEDGER_OUT therefore exposes every balance point as a LedgerBalance carrying
(`debit`, `credit`, `side`) with one always zero (both zero when the account is
even), so the UI can render "Dr 50,000" or "Cr 30,000" directly.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class LedgerBalance(BaseModel):
    """A balance shown the way a real ledger shows it: as an unsigned figure on
    one side. `debit` and `credit` are mutually exclusive (one is always zero;
    both are zero when flat). `side` is 'debit' | 'credit' | 'zero'."""

    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    side: str = "zero"


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
    running_balance: LedgerBalance
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
    opening_balance: LedgerBalance
    debit_movements: Decimal
    credit_movements: Decimal
    closing_balance: LedgerBalance
    movements: list[LedgerMovementOut] = []