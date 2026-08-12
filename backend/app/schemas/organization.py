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
    created_at: datetime


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