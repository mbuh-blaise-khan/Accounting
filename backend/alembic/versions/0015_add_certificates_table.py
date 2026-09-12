"""0015 - Certificates table (Session 11 Part B1)."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "certificates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("course_slug", sa.String(50), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "wording",
            sa.String(200),
            nullable=False,
            server_default="Kinxta Docu Certificate of Completion",
        ),
        sa.UniqueConstraint(
            "user_id", "course_slug", name="uq_certificate_user_course"
        ),
    )
    op.create_index("ix_certificates_user_id", "certificates", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_certificates_user_id", table_name="certificates")
    op.drop_table("certificates")
