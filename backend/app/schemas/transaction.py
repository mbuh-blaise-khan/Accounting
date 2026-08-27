"""Pydantic schemas for transaction entry and posting."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TransactionLineIn(BaseModel):
    """One debit-or-credit line of a transaction.

    Each line is either a debit or a credit (exactly one side is positive).
    Amounts are non-negative. The overall balance (sum debits == sum credits)
    is required only at posting time — drafts may be unbalanced while building.
    `narration` is the optional per-line description ("libellé").
    """

    account_id: int
    debit: Decimal = Field(default=Decimal(0))
    credit: Decimal = Field(default=Decimal(0))
    narration: Optional[str] = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def _check_line(self):
        if self.debit < 0 or self.credit < 0:
            raise ValueError("Amounts must be non-negative")
        # Exactly one side must be positive (double entry): not both, not neither.
        if (self.debit > 0) == (self.credit > 0):
            raise ValueError(
                "Each line must be a debit OR a credit — not both or neither"
            )
        return self


class TransactionCreate(BaseModel):
    organization_id: int
    description: str = Field(min_length=1, max_length=2000)
    lines: list[TransactionLineIn] = Field(min_length=2, max_length=20)


class TransactionLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    debit_amount: Decimal
    credit_amount: Decimal
    narration: Optional[str] = None
    # Denormalized display fields (filled by the serializer from the account).
    account_code: Optional[str] = None
    account_name_en: Optional[str] = None
    account_name_fr: Optional[str] = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    description: str
    status: str
    posted_at: Optional[datetime] = None
    created_at: datetime
    # When this transaction is a completed reversing entry, this is the id of
    # the original posted transaction it mirrors (NULL otherwise).
    reverse_of_id: Optional[int] = None
    lines: list[TransactionLineOut] = []