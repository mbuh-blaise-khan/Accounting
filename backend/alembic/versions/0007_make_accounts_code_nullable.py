"""make accounts.code nullable (IFRS accounts have no code)

Session 7, Part B: IFRS does not mandate a numbered chart of accounts (only a
small set of jurisdictions — France, Germany, China, Russia and OHADA member
states — legally require one). IFRS accounts therefore never carry a code; the
shared `accounts.code` column is kept for the OHADA side and stored NULL for
IFRS. The existing unique constraint (organization_id, framework, code) already
permits multiple NULLs, so many IFRS accounts can coexist without codes.

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "accounts",
        "code",
        existing_type=sa.String(20),
        nullable=True,
    )


def downgrade() -> None:
    # OHADA codes remain; any NULL codes (IFRS) are set to '' as a best effort
    # so the NOT NULL constraint can be restored without losing rows.
    op.execute("UPDATE accounts SET code = '' WHERE code IS NULL")
    op.alter_column(
        "accounts",
        "code",
        existing_type=sa.String(20),
        nullable=False,
    )
