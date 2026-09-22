"""add nullable archived_at to organizations (workspace archive / restore)

Archive-first product policy: archiving a workspace HIDES it from the default
active "Your Workspaces" list and makes it read-only at the service layer,
but DELETES NOTHING — the business profile (all of which lives directly on
this table), accounts, drafts, posted transactions, reports and memberships
all stay intact. NULL means active, so every organization that exists at
migration time is active by default — no backfill needed and no behavior
change for existing workspaces.

Retention note: IFRS and OHADA do NOT define one universal record-retention
period — retention duties vary by jurisdiction and applicable commercial,
tax, audit and sector rules. Archive-first is used here because this project
treats posted accounting records as immutable.

Revision ID: 0019
Revises: 0018
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "archived_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment=(
                "NULL = active workspace. Set when the owner archives the "
                "workspace (read-only at the service layer, hidden from the "
                "active list); cleared on restore. Nothing is deleted by "
                "archiving."
            ),
        ),
    )


def downgrade() -> None:
    op.drop_column("organizations", "archived_at")
