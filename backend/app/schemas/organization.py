"""Pydantic schemas for organizations and frameworks."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AccountingBasis, FrameworkCode, IdentityType, OrgPurpose


# --- Organizations ------------------------------------------------------------

class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    framework: FrameworkCode
    currency: str = "XAF"
    is_demo: bool = False


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    owner_user_id: int
    framework: str
    currency: str
    is_demo: bool
    # Optional Business Profile (all-optional except the fiscal-year month,
    # which defaults to January / calendar year for period math).
    registered_address: Optional[str] = None
    rccm_number: Optional[str] = None
    tax_id: Optional[str] = None
    fiscal_year_start_month: int = 1
    # Server-side marker of the mandatory Business-Profile step: False for new
    # workspaces (the UI hard-gates until the profile is saved), True for
    # pre-mandate orgs (migration 0011 backfill) and once saved.
    profile_completed: bool = False
    # Identity (Business Profile Part 2) — all optional in the DATA; which of
    # them are REQUIRED is decided by identity_type (see update_business_profile).
    identity_type: Optional[str] = None
    country: Optional[str] = None
    legal_form: Optional[str] = None
    # Business Profile Session 2 — all optional; accounting_basis defaults to
    # 'accrual' and is informational-only (never affects computations).
    org_purpose: Optional[str] = None
    business_activity: Optional[str] = None
    accounting_basis: str = "accrual"
    company_description: Optional[str] = None
    created_at: datetime


class OrganizationUpdate(BaseModel):
    """Partial update of the Business Profile (all fields optional; empty
    strings are normalized to NULL on the service side so users can clear a
    value they previously entered).

    framework is DELIBERATELY ABSENT: it is immutable after creation (Business
    Profile Part 2 decision — switching OHADA<->IFRS would invalidate the whole
    seeded chart of accounts). Any attempt to send it is ignored here and the
    service layer additionally rejects framework changes explicitly.
    """

    registered_address: Optional[str] = Field(default=None, max_length=2000)
    rccm_number: Optional[str] = Field(default=None, max_length=80)
    tax_id: Optional[str] = Field(default=None, max_length=80)
    fiscal_year_start_month: Optional[int] = Field(
        default=None, ge=1, le=12, description="1-12, defaults to 1 (January)"
    )
    identity_type: Optional[IdentityType] = None
    country: Optional[str] = Field(
        default=None, min_length=2, max_length=2,
        description="ISO 3166-1 alpha-2 code (OHADA: one of the 17 member states)",
    )
    legal_form: Optional[str] = Field(default=None, max_length=40)
    # Business Profile Session 2 — every field OPTIONAL (never blocks saving).
    # accounting_basis is informational-only metadata and has ZERO effect on
    # posting/ledger/statement logic (the engine is accrual-based).
    org_purpose: Optional[OrgPurpose] = None
    business_activity: Optional[str] = Field(
        default=None, max_length=120,
        description="Category code, or the free-text description when 'Other' is chosen",
    )
    accounting_basis: Optional[AccountingBasis] = None
    company_description: Optional[str] = Field(default=None, max_length=1000)


# --- Identity options (dropdown data for the Business Profile form) -----------

class CountryOptionOut(BaseModel):
    code: str
    name_en: str
    name_fr: str


class LegalFormOptionOut(BaseModel):
    code: str
    label: str
    description_en: str
    description_fr: str


class IdentityOptionsOut(BaseModel):
    """Country + legal-form options for ONE framework: OHADA gets only its 17
    member states and the AUSCGIE forms; IFRS gets the full international
    country list and the international forms."""

    countries: list[CountryOptionOut]
    legal_forms: list[LegalFormOptionOut]


# --- Frameworks ---------------------------------------------------------------

class FrameworkVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_label: str
    is_current: bool
    description: str


class FrameworkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description_en: str
    description_fr: str
    is_active: bool
    versions: list[FrameworkVersionOut] = []