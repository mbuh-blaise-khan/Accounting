"""0016 - Certificate verification fields (Session 11 Part B3).

Adds, to the B1 `certificates` table:
- credential_id: unique, unguessable public credential identifier. This is the
  ONLY identifier accepted by the public verification endpoint; the sequential
  integer PK is never a credential and never returned publicly.
- status: 'valid' | 'revoked' lifecycle state (revoked rows are never deleted).
- recipient_name: display-name snapshot taken at issuance so public
  verification never touches the users table (no email/user-id leakage).

Backfill: existing rows get credential_id='LEGACY-<id>' and status='valid'.
New issuance always writes a secrets.token_urlsafe credential id instead.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "certificates",
        sa.Column("credential_id", sa.String(64), nullable=True),
    )
    op.add_column(
        "certificates",
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="valid",
        ),
    )
    op.add_column(
        "certificates",
        sa.Column(
            "recipient_name",
            sa.String(120),
            nullable=False,
            server_default="",
        ),
    )
    # Backfill any B1/B2-era rows (they have no credential ids yet). The
    # LEGACY- prefix keeps them deterministic and auditable; real issuance
    # always generates a secrets.token_urlsafe value instead.
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE certificates SET credential_id = ('LEGACY-' || id) "
            "WHERE credential_id IS NULL"
        )
    )
    conn.execute(sa.text("UPDATE certificates SET status = 'valid' WHERE status IS NULL"))
    conn.execute(
        sa.text(
            "UPDATE certificates SET recipient_name = '' WHERE recipient_name IS NULL"
        )
    )
    op.alter_column("certificates", "credential_id", nullable=False)
    op.create_unique_constraint(
        "uq_certificate_credential_id", "certificates", ["credential_id"]
    )
    op.create_index(
        "ix_certificates_credential_id", "certificates", ["credential_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_certificates_credential_id", table_name="certificates")
    op.drop_constraint(
        "uq_certificate_credential_id", "certificates", type_="unique"
    )
    op.drop_column("certificates", "recipient_name")
    op.drop_column("certificates", "status")
    op.drop_column("certificates", "credential_id")