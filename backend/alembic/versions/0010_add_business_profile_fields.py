"""add optional Business Profile fields to organizations

Session: Business Profile (Post-S9 report polish).

All choices are OPTIONAL (registered_address, rccm_number, tax_id) so every
existing workspace stays valid with them NULL — not every user owns a fully
registered business. fiscal_year_start_month is the one real default: period
math ALWAYS needs a starting month, so it defaults to January (calendar year)
via server_default '1' and is non-nullable; existing rows become '1'.

These fields feed (a) the Business Profile settings page and (b) the legal
identifiers (RCCM, tax id) shown on official-style financial document headers,
per docs/ohada-ifrs-source-reference.md research (RCCM number + country tax id
belong on OHADA-area documents).

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("registered_address", sa.Text(), nullable=True))
    op.add_column("organizations", sa.Column("rccm_number", sa.String(length=80), nullable=True))
    op.add_column("organizations", sa.Column("tax_id", sa.String(length=80), nullable=True))
    op.add_column(
        "organizations",
        sa.Column(
            "fiscal_year_start_month", sa.Integer(), nullable=False, server_default="1"
        ),
    )


def downgrade() -> None:
    op.drop_column("organizations", "fiscal_year_start_month")
    op.drop_column("organizations", "tax_id")
    op.drop_column("organizations", "rccm_number")
    op.drop_column("organizations", "registered_address")