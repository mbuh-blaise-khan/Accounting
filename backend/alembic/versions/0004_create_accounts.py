"""create accounts table

Session 5: chart of accounts.

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "organization_id",
            sa.Integer(),
            sa.ForeignKey("organizations.id"),
            nullable=False,
        ),
        sa.Column(
            "framework",
            sa.Enum("OHADA", "IFRS", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name_en", sa.String(length=160), nullable=False),
        sa.Column("name_fr", sa.String(length=160), nullable=False),
        sa.Column(
            "account_class",
            sa.Enum(
                "asset", "liability", "equity", "revenue", "expense",
                native_enum=False, length=20,
            ),
            nullable=False,
        ),
        sa.Column(
            "parent_account_id",
            sa.Integer(),
            sa.ForeignKey("accounts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "normal_balance",
            sa.Enum("debit", "credit", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column(
            "is_system_default",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "organization_id", "framework", "code",
            name="uq_account_org_framework_code",
        ),
    )
    op.create_index(op.f("ix_accounts_organization_id"), "accounts", ["organization_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_accounts_organization_id"), table_name="accounts")
    op.drop_table("accounts")
