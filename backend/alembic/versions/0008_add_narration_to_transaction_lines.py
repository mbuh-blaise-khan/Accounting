"""add narration to transaction_lines

Session 7: the Journal shows a per-line narration ("libellé" in the journal
entry grid). The UI already collects it; this migration persists it so the
Journal can display it.

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transaction_lines",
        sa.Column("narration", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transaction_lines", "narration")
