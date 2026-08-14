"""Chart of accounts model.

The `accounts` table holds one chart per organization. Each account belongs to a
framework context (OHADA or IFRS) which must match the owning organization's
framework. Only the illustrative/demo chart (see services/account_service.py) is
seeded — it is NOT an official chart and must be replaced before any real
production or compliance use.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import AccountClass, FrameworkCode, NormalBalance


class Account(Base):
    """A single account in an organization's chart of accounts."""

    __tablename__ = "accounts"
    __table_args__ = (
        # A code is unique within an organization + framework context.
        UniqueConstraint(
            "organization_id", "framework", "code", name="uq_account_org_framework_code"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    framework: Mapped[str] = mapped_column(
        Enum(FrameworkCode, native_enum=False, length=10), nullable=False
    )
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name_en: Mapped[str] = mapped_column(String(160), nullable=False)
    name_fr: Mapped[str] = mapped_column(String(160), nullable=False)
    account_class: Mapped[str] = mapped_column(
        Enum(AccountClass, native_enum=False, length=20), nullable=False
    )
    # Optional parent for grouping/rollup (flat illustrative chart has none).
    parent_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    normal_balance: Mapped[str] = mapped_column(
        Enum(NormalBalance, native_enum=False, length=10), nullable=False
    )
    # True for the seeded illustrative accounts (demo data); False for
    # user-created custom accounts.
    is_system_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    # Soft-delete flag: inactive accounts are hidden from posting flows but kept.
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
