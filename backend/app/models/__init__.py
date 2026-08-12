"""Import models here so Alembic autogenerate sees every table's metadata."""
from app.models.enums import FrameworkCode, MembershipRole  # noqa: F401
from app.models.framework import Framework, FrameworkVersion  # noqa: F401
from app.models.organization import Organization, OrganizationMember  # noqa: F401
from app.models.user import LanguagePreference, User  # noqa: F401
