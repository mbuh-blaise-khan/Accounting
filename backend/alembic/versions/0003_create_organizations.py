"""create organizations, organization_members, frameworks, framework_versions

Session 4: workspaces + framework registry.

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "framework",
            sa.Enum("OHADA", "IFRS", native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column("currency", sa.String(length=10), server_default="XAF", nullable=False),
        sa.Column("is_demo", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_organizations_owner_user_id"), "organizations", ["owner_user_id"])

    op.create_table(
        "organization_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "role",
            sa.Enum("owner", "member", native_enum=False, length=20),
            server_default="member",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("org_id", "user_id", name="uq_org_user"),
    )
    op.create_index(op.f("ix_organization_members_org_id"), "organization_members", ["org_id"])

    op.create_table(
        "frameworks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.Enum("OHADA", "IFRS", native_enum=False, length=10), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description_en", sa.Text(), server_default="", nullable=False),
        sa.Column("description_fr", sa.Text(), server_default="", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code", name="uq_frameworks_code"),
    )

    op.create_table(
        "framework_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("framework_id", sa.Integer(), sa.ForeignKey("frameworks.id"), nullable=False),
        sa.Column("version_label", sa.String(length=80), nullable=False),
        sa.Column("is_current", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_framework_versions_framework_id"), "framework_versions", ["framework_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_framework_versions_framework_id"), table_name="framework_versions")
    op.drop_table("framework_versions")
    op.drop_table("frameworks")
    op.drop_index(op.f("ix_organization_members_org_id"), table_name="organization_members")
    op.drop_table("organization_members")
    op.drop_index(op.f("ix_organizations_owner_user_id"), table_name="organizations")
    op.drop_table("organizations")