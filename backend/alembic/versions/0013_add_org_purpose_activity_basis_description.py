"""0013 — Business Profile Session 2: org_purpose, business_activity,
accounting_basis, company_description.

All four are optional per the spec — every organization created before this
migration stays valid with them unset. The one nuance: accounting_basis is
informational-only metadata with a real default of 'accrual' (accentuated:
a basis ALWAYS exists implicitly even when the user never picks one), so the
column is NOT NULL with a server default that backfills existing rows.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("org_purpose", sa.String(40), nullable=True))
    op.add_column("organizations", sa.Column("business_activity", sa.String(120), nullable=True))
    op.add_column(
        "organizations",
        sa.Column("accounting_basis", sa.String(20), nullable=False, server_default="accrual"),
    )
    op.add_column("organizations", sa.Column("company_description", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("organizations", "company_description")
    op.drop_column("organizations", "accounting_basis")
    op.drop_column("organizations", "business_activity")
    op.drop_column("organizations", "org_purpose")