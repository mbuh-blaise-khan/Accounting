"""0012 — Business Profile Part 2: identity_type, country, legal_form.

All three are NULLABLE on purpose: organizations created before this change
must remain valid with these fields unset (the mandatory Business-Profile
flow is a frontend/API rule, not a database constraint). Values:
- identity_type: 'learner' | 'unregistered_business' | 'registered_business'
- country:       ISO 3166-1 alpha-2 code; for OHADA workspaces only the 17
                 member states are accepted at the API layer
- legal_form:    framework-specific code (AUSCGIE forms for OHADA) or
                 'NOT_APPLICABLE' for learning-only workspaces
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("identity_type", sa.String(40), nullable=True))
    op.add_column("organizations", sa.Column("country", sa.String(2), nullable=True))
    op.add_column("organizations", sa.Column("legal_form", sa.String(40), nullable=True))


def downgrade() -> None:
    op.drop_column("organizations", "legal_form")
    op.drop_column("organizations", "country")
    op.drop_column("organizations", "identity_type")