"""Shared enums for frameworks and memberships."""
import enum


class FrameworkCode(str, enum.Enum):
    """Accounting frameworks supported as separate, configurable contexts."""
    OHADA = "OHADA"
    IFRS = "IFRS"
    # Additional frameworks (e.g. local GAAPs) can be added later.


class MembershipRole(str, enum.Enum):
    owner = "owner"
    member = "member"


class AccountClass(str, enum.Enum):
    """High-level, plain-language account groups (kept non-accountant friendly).

    These are NOT the numbered OHADA classes (1-8) — this is illustrative demo
    data only. The account_class drives how the Chart of Accounts page groups
    accounts and how normal_balance is inferred in the seed.
    """

    asset = "asset"
    liability = "liability"
    equity = "equity"
    revenue = "revenue"
    expense = "expense"


class NormalBalance(str, enum.Enum):
    """The side an account normally increases on (debit or credit)."""

    debit = "debit"
    credit = "credit"


class TransactionStatus(str, enum.Enum):
    """Lifecycle of a transaction.

    draft   -> editable, not yet verified/posted
    posted  -> balanced, immutable (only correctable via a reversal)
    reversed-> a reversing entry has been applied (stub in Session 6)
    """

    draft = "draft"
    posted = "posted"
    reversed = "reversed"