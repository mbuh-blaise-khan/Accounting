"""Certificate model for learning course completion (Session 11 Part B1)."""

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Certificate(Base):
    """One certificate per (user, course); idempotent issuance (Part B1)."""

    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    course_slug: Mapped[str] = mapped_column(String(50), nullable=False)
    # Public, unguessable credential identifier (Session 11 Part B3). This is
    # the ONLY identifier ever exposed to public verification — the sequential
    # integer PK (id) is never accepted as a credential and never returned
    # publicly. Unique across all certificates.
    credential_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    # Lifecycle status (Session 11 Part B3): 'valid' | 'revoked'. Revoked
    # certificates are NEVER deleted; they still resolve publicly but render
    # with a "no longer valid" treatment. Any unknown value renders as
    # revoked-safe on the public side (fail closed, never valid).
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="valid")
    # Recipient display-name snapshot taken at issuance (Session 11 Part B3).
    # Denormalized on purpose: the public verification response must work
    # without ever touching the users table (no email/user-id leakage).
    recipient_name: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    # Wording is fixed per the Part B1 spec (no other strings are added).
    wording: Mapped[str] = mapped_column(String(200), nullable=False)

    user: Mapped["User"] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "course_slug", name="uq_certificate_user_course"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Certificate {self.id} user={self.user_id} course={self.course_slug}>"
