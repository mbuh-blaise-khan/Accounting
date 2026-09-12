"""Pydantic schemas for certificates (Session 11 Part B1)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CertificateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    course_slug: str
    issued_at: datetime
    wording: str
