"""Pydantic schemas for the chart of accounts."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AccountClass, FrameworkCode, NormalBalance


class AccountCreate(BaseModel):
    """Payload for a user-created custom account.

    is_system_default is always False for custom accounts (system default is
    set only by the seed). framework must match the organization's framework
    and is validated in the service layer.
    """

    organization_id: int
    framework: FrameworkCode
    code: str = Field(min_length=1, max_length=20)
    name_en: str = Field(min_length=1, max_length=160)
    name_fr: str = Field(min_length=1, max_length=160)
    account_class: AccountClass
    parent_account_id: Optional[int] = None
    normal_balance: NormalBalance
    description: str = Field(default="", max_length=2000)


class AccountUpdate(BaseModel):
    """Optional fields for PATCH /accounts/{id}.

    Editing a system-default account is restricted to the `active` flag and
    plain-language names (code/class/balance are structural and locked).
    """

    name_en: Optional[str] = Field(default=None, min_length=1, max_length=160)
    name_fr: Optional[str] = Field(default=None, min_length=1, max_length=160)
    active: Optional[bool] = None


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    framework: str
    code: str
    name_en: str
    name_fr: str
    account_class: str
    parent_account_id: Optional[int] = None
    normal_balance: str
    is_system_default: bool
    active: bool
    description: str
    created_at: datetime