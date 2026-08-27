"""add reverse_of_id to transactions and created_by to accounts

Session: post-Session-8 fixes.

- transactions.reverse_of_id: a nullable self-referential FK so a completed
  reversing entry links back to the original posted transaction it mirrors.
  The original record is never edited/deleted (immutability rule) — it is only
  marked `reversed`; the new, opposite entry holds this pointer.

- accounts.created_by: a nullable FK to users.id so we can tell which
  workspace member personally created a custom account (used for smart
  ordering in the General Ledger account dropdown).

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("reverse_of_id", sa.Integer(), sa.ForeignKey("transactions.id"), nullable=True, index=True),
    )
    op.add_column(
        "accounts",
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("accounts", "created_by")
    op.drop_column("transactions", "reverse_of_id")