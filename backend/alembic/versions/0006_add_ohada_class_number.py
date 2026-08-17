"""add ohada_class_number to accounts

Session 6b: real OHADA class (1-9) on accounts for standards-compliant chart.

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "accounts",
        sa.Column("ohada_class_number", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("accounts", "ohada_class_number")