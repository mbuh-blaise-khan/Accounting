"""Pydantic schemas for user/auth endpoints."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import LanguagePreference


class UserBase(BaseModel):
    email: str
    display_name: str = Field(min_length=1, max_length=120)
    language_preference: LanguagePreference = LanguagePreference.en


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    language_preference: Optional[LanguagePreference] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str
    language_preference: LanguagePreference
    created_at: datetime
