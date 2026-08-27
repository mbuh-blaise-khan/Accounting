"""Pydantic schemas for the Trial Balance (Session 9).

ONE computation, THREE views: every row always carries its opening balance,
period movement and closing balance, each split into debit/credit columns.
The `columns` query parameter (2|4|6) is a VIEW choice — the API response is
identical regardless (the frontend re-renders without refetching), so a
beginner can switch between the simple 2-column and the detailed 6-column
layout instantly.

Column-placement convention (classic trial balance): each figure sits on the
side where its NET actually lies — net debit → Debit column, net credit →
Credit column. This is independent of the account's normal_balance (e.g. an
overdrawn cash account shows a CREDIT balance in the trial balance).
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class TrialBalanceRowOut(BaseModel):
    """One account's trial-balance figures across all three views."""

    account_id: int
    code: Optional[str] = None  # OHADA only; IFRS accounts have no code
    name_en: str
    name_fr: str
    normal_balance: str  # 'debit' | 'credit' (for ledger drill-down context)
    opening_debit: Decimal = Decimal("0")
    opening_credit: Decimal = Decimal("0")
    movement_debit: Decimal = Decimal("0")
    movement_credit: Decimal = Decimal("0")
    closing_debit: Decimal = Decimal("0")
    closing_credit: Decimal = Decimal("0")


class TrialBalanceTotalsOut(BaseModel):
    """Column totals. closing_debit == closing_credit MUST hold for any set of
    balanced double-entry transactions (posted + reversed); if not, that is a
    serious bug surfaced loudly by the UI, not hidden."""

    opening_debit: Decimal = Decimal("0")
    opening_credit: Decimal = Decimal("0")
    movement_debit: Decimal = Decimal("0")
    movement_credit: Decimal = Decimal("0")
    closing_debit: Decimal = Decimal("0")
    closing_credit: Decimal = Decimal("0")


class TrialBalanceOut(BaseModel):
    """The full report for one organization. All figures are DERIVED from
    posted + reversed journal lines on every call — nothing stored. Rows with
    zero activity at every level are omitted (a cleaner report for learners;
    their absence is exactly equivalent to displaying zeros)."""

    date_from: Optional[date] = None  # period start (None = all time)
    as_of: Optional[date] = None  # period end (None = now/everything)
    columns: int = 2  # requested VIEW: 2 | 4 | 6 (payload is view-independent)
    rows: list[TrialBalanceRowOut] = []
    totals: TrialBalanceTotalsOut
    balanced: bool  # True when closing debits == closing credits
