"""Pydantic schemas for the Journal and Cash Book (Session 7)."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class JournalEntryOut(BaseModel):
    """One posted transaction LINE as shown in the Journal / Cash Book.

    A posted transaction is expanded into one row per transaction line. The
    row's date is the transaction's real `posted_at` timestamp (Part C) — the
    first column everywhere a posted transaction is shown. `account_code` is
    NULL for IFRS workspaces (Part B: IFRS accounts have no code), so the
    frontend omits the account-number column for IFRS.
    """

    id: int  # transaction_line.id (drill-down key)
    transaction_id: int
    date: Optional[datetime] = None  # posted_at
    reference: str
    description: str
    account_id: int
    account_code: Optional[str] = None
    account_name_en: Optional[str] = None
    account_name_fr: Optional[str] = None
    debit: Decimal
    credit: Decimal
    narration: Optional[str] = None
    source: str = "manual"
    status: str = "posted"
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    # Cash Book only: explicit account bucket used by the single/double layouts.
    cashbook_type: Optional[str] = None  # "cash" or "bank"
