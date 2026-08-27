"""Transaction and transaction-line models.

Double-entry integrity is enforced both in the database (non-negative line
amounts, a line cannot be both zero) and in the service layer (>=2 lines and
total debits == total credits before a transaction can be posted). A posted or
reversed transaction is immutable — corrections happen via reversing entries.
"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.account import Account
from app.models.enums import TransactionStatus


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    # The plain-language description of what happened (beginner-friendly).
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(TransactionStatus, native_enum=False, length=10),
        default=TransactionStatus.draft,
        nullable=False,
    )
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    lines: Mapped[list["TransactionLine"]] = relationship(
        back_populates="transaction",
        cascade="all, delete-orphan",
        order_by="TransactionLine.id",
    )
    # If this transaction is a completed reversing entry, `reverse_of_id` points
    # at the original posted transaction it mirrors (never edited/deleted).
    reverse_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("transactions.id"), nullable=True, index=True
    )


class TransactionLine(Base):
    __tablename__ = "transaction_lines"
    __table_args__ = (
        CheckConstraint(
            "debit_amount >= 0 AND credit_amount >= 0",
            name="ck_line_amounts_non_negative",
        ),
        CheckConstraint(
            "NOT (debit_amount = 0 AND credit_amount = 0)",
            name="ck_line_at_least_one_side",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"), nullable=False, index=True
    )
    debit_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 2), default=Decimal(0), nullable=False
    )
    credit_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 2), default=Decimal(0), nullable=False
    )
    # Per-line narration ("libellé" in the journal grid / Journal column).
    narration: Mapped[str | None] = mapped_column(String(255), nullable=True)

    transaction: Mapped["Transaction"] = relationship(back_populates="lines")
    # For eager loading of account names when serializing.
    account: Mapped[Account] = relationship()