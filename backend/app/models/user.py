"""User model.

IMPORTANT: only English/French are wired in the MVP. The language_preference
column is stored as an enum value but designed so "pidgin" and other languages
can be added later without a schema change (SQLAlchemy Enum, not a native PG
enum, making it cheap to extend).
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LanguagePreference(str, enum.Enum):
    en = "en"
    fr = "fr"
    # Pidgin and other languages can be added here later (future scope).


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    language_preference: Mapped[str] = mapped_column(
        Enum(LanguagePreference, native_enum=False, length=10),
        default=LanguagePreference.en,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
