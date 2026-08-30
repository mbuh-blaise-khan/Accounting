"""Pydantic response schemas for the financial statements (Session 10, Part A).

The statements are DERIVED from posted journal lines on every call (never
stored). A single account line carries its code (OHADA SYSCOHIDA numbering)
or name (IFRS), both-language labels, and a positive monetary amount.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class StatementLine(BaseModel):
    """One account line within a statement section."""

    code: Optional[str] = None  # OHADA only; IFRS accounts carry no code
    name_en: str
    name_fr: str
    amount: Decimal = Decimal("0")
    # result/extraordinary line sign: 'revenue'/'expense'/'extraordinary'.
    # Omitted on balance-sheet accounts (their amount is always positive).
    type: Optional[str] = None


class StatementSection(BaseModel):
    """A labelled group of lines (e.g. 'Revenue', 'Actif', 'Capitaux propres')."""

    key: str
    label_en: str
    label_fr: str
    lines: list[StatementLine] = []
    total: Decimal = Decimal("0")


class IncomeStatementOut(BaseModel):
    framework: str
    statement_name_en: str  # e.g. "Compte de résultat" / "Statement of Profit or Loss"
    statement_name_fr: str
    currency: str
    date_from: Optional[date] = None  # period start (None = all history to as_of)
    as_of: Optional[date] = None  # period end (None = open-ended / all history)
    sections: list[StatementSection]
    revenue_total: Decimal
    expense_total: Decimal
    extraordinary_total: Optional[Decimal] = Decimal("0")  # OHADA-only (class 8)
    ordinary_result: Decimal
    net_result: Decimal


class FinancialPositionOut(BaseModel):
    framework: str
    statement_name_en: str  # "Bilan" / "Statement of Financial Position"
    statement_name_fr: str
    currency: str
    as_of: Optional[date] = None  # statement date (None = all history to now)
    sections: list[StatementSection]
    assets: Decimal
    liabilities: Decimal
    equity: Decimal
    balanced: bool  # True when assets == liabilities + equity
