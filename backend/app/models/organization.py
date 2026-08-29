"""Organization / workspace model and membership model."""
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
from app.models.enums import FrameworkCode, MembershipRole


class Organization(Base):
    """A user's workspace. Currency is stored explicitly (default XAF)."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    owner_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    # IMMUTABLE after creation (Business Profile Part 2 decision): the entire
    # seeded chart of accounts (OHADA SYSCOHADA subset / IFRS IAS-1 template,
    # seeded since Session 6b) is framework-specific. Letting OHADA<->IFRS be
    # switched post-creation would invalidate every seeded account and every
    # posted line, so NO edit path exists anywhere: the field is deliberately
    # absent from OrganizationUpdate, and the service rejects any attempt to
    # change it (belt-and-braces guard in organization_service).
    framework: Mapped[str] = mapped_column(
        Enum(FrameworkCode, native_enum=False, length=10), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(10), default="XAF", nullable=False)
    # True when created via the "use a sample demo business" button.
    # The demo chart-of-accounts seed data arrives in Session 5.
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # --- Optional Business Profile (Session: Business Profile). All-optional:
    # not every workspace is a fully-registered business, so existing/ignored
    # workspaces stay valid with these null. Only fiscal_year_start_month has a
    # real default (January / calendar year) because period math ALWAYS needs a
    # starting month to compute an "opening" point.
    registered_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    rccm_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    fiscal_year_start_month: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False
    )
    # Server-side marker of the MANDATORY Business-Profile step: False for
    # every NEWLY created workspace (the UI hard-gates features until the
    # profile is saved), True once the blocking fields exist. Migration 0011
    # backfills True for every PRE-MANDATE org so existing workspaces are
    # never hard-blocked (banner instead).
    profile_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    # --- Identity (Business Profile Part 2). ALL NULLABLE on purpose:
    # organizations created before this change must remain valid with these
    # unset (the mandate is a frontend/API rule, not a DB constraint).
    # identity_type decides which OTHER profile fields are required — see
    # app.accounting.identity_reference and frontend/src/utils/profile.js.
    # - identity_type: 'learner' | 'unregistered_business' | 'registered_business'
    # - country:       ISO 3166-1 alpha-2 code (OHADA workspaces: one of the
    #                  17 member states, validated at the API layer)
    # - legal_form:    framework-specific code (AUSCGIE forms for OHADA) or
    #                  'NOT_APPLICABLE' for learning-only workspaces
    identity_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    legal_form: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # --- Business Profile Session 2: purpose, activity, basis, description. ---
    # ALL optional at the DB level (backward compatibility — existing orgs
    # remain valid with these unset) EXCEPT accounting_basis, which is
    # informational-only metadata with a default of 'accrual' (a basis always
    # exists implicitly even when the user never chooses). IMPORTANT
    # constraint, enforced by test: accounting_basis has ZERO effect on any
    # posting / ledger / statement computation — the engine is accrual-based
    # and this field is never read by transaction logic.
    org_purpose: Mapped[str | None] = mapped_column(String(40), nullable=True)
    business_activity: Mapped[str | None] = mapped_column(String(120), nullable=True)
    accounting_basis: Mapped[str] = mapped_column(
        String(20), default="accrual", server_default="accrual", nullable=False
    )
    company_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class OrganizationMember(Base):
    """Membership join: which users belong to which organization and with what role."""

    __tablename__ = "organization_members"
    __table_args__ = (UniqueConstraint("org_id", "user_id", name="uq_org_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum(MembershipRole, native_enum=False, length=20),
        default=MembershipRole.member,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
