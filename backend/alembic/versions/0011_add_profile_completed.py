"""add profile_completed flag to organizations (mandatory Business Profile step)

The Business Profile is no longer purely optional: NEW workspaces must complete
it before using the workspace's features (with a learner exemption for the
RCCM/tax ID). The profile columns themselves stay NULLABLE — the mandate is
expressed by this boolean flag instead:

- New organizations start at False (hard-gated in the UI).
- Saving the profile sets it True server-side when the blocking fields
  (registered_address + fiscal_year_start_month) exist.
- Every organization that exists AT MIGRATION TIME was created before the
  mandate (the fields were optional then) and is backfilled to True so
  existing workspaces are never hard-blocked — they get a dismissible
  completion banner instead.

A persistent flag is needed because an in-memory/session marker would reset on
page reload, letting a brand-new workspace dodge the mandate entirely.

Revision ID: 0011
Revises: 0010
Create Date: 2026-08-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "profile_completed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
            comment=(
                "True once the mandatory Business Profile step is done, or the "
                "org predates the mandate (never hard-block legacy workspaces)."
            ),
        ),
    )
    # Pre-mandate backfill — see module docstring.
    op.execute("UPDATE organizations SET profile_completed = true")


def downgrade() -> None:
    op.drop_column("organizations", "profile_completed")