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
    # Public credential id + lifecycle status (Part B3). The private schema
    # keeps user_id (needed by the authed UI); the PUBLIC schema below is a
    # separate, privacy-safe model that never carries user_id, email, or id.
    credential_id: str
    status: str
    recipient_name: str


class PublicCertificateOut(BaseModel):
    """Privacy-safe public verification response (Session 11 Part B3).

    Deliberately separate from CertificateOut: no internal `id`, no `user_id`,
    no email, no workspace/transaction/answer data of any kind. The ONLY
    personal datum is the display-name snapshot taken at issuance.
    """

    model_config = ConfigDict(from_attributes=True)

    credential_id: str
    status: str  # 'valid' | 'revoked'
    issuer: str
    wording: str
    recipient_name: str
    course_title: str
    course_slug: str
    issued_at: datetime
    completed_at: datetime
    verification_url: str | None = None
