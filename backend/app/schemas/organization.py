"""Pydantic schemas for organizations and frameworks."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FrameworkCode


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
    created_at: datetime


class OrganizationUpdate(BaseModel):
    """Partial update of the Business Profile (all fields optional; empty
    strings are normalized to NULL on the service side so users can clear a
    value they previously entered)."""

    registered_address: Optional[str] = Field(default=None, max_length=2000)
    rccm_number: Optional[str] = Field(default=None, max_length=80)
    tax_id: Optional[str] = Field(default=None, max_length=80)
    fiscal_year_start_month: Optional[int] = Field(
        default=None, ge=1, le=12, description="1-12, defaults to 1 (January)"
    )


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