"""Shared enums for frameworks and memberships."""
import enum


class FrameworkCode(str, enum.Enum):
    """Accounting frameworks supported as separate, configurable contexts."""
    OHADA = "OHADA"
    IFRS = "IFRS"
    # Additional frameworks (e.g. local GAAPs) can be added later.


class MembershipRole(str, enum.Enum):
    owner = "owner"
    member = "member"