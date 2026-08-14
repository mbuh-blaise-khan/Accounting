"""create transactions and transaction_lines tables

Session 6: first transaction entry and posting.

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "organization_id",
            sa.Integer(),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "posted", "reversed", native_enum=False, length=10),
            server_default="draft",
            nullable=False,
        ),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_transactions_organization_id"), "transactions", ["organization_id"]
    )

    op.create_table(
        "transaction_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "transaction_id",
            sa.Integer(),
            sa.ForeignKey("transactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=False
        ),
        sa.Column("debit_amount", sa.Numeric(16, 2), server_default="0", nullable=False),
        sa.Column("credit_amount", sa.Numeric(16, 2), server_default="0", nullable=False),
        sa.CheckConstraint(
            "debit_amount >= 0 AND credit_amount >= 0",
            name="ck_line_amounts_non_negative",
        ),
        sa.CheckConstraint(
            "NOT (debit_amount = 0 AND credit_amount = 0)",
            name="ck_line_at_least_one_side",
        ),
    )
    op.create_index(
        op.f("ix_transaction_lines_transaction_id"),
        "transaction_lines",
        ["transaction_id"],
    )
    op.create_index(
        op.f("ix_transaction_lines_account_id"), "transaction_lines", ["account_id"]
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_transaction_lines_account_id"), table_name="transaction_lines"
    )
    op.drop_index(
        op.f("ix_transaction_lines_transaction_id"), table_name="transaction_lines"
    )
    op.drop_table("transaction_lines")
    op.drop_index(op.f("ix_transactions_organization_id"), table_name="transactions")
    op.drop_table("transactions")