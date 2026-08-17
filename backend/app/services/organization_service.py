"""Organization (workspace) service.

Logic lives here (not in the endpoint) so it is independently testable:
- creating an org always attaches the creator as an owner member,
- listing/getting is always scoped to the current user's memberships.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import FrameworkCode, MembershipRole
from app.models.organization import Organization, OrganizationMember
from app.models.user import User

DEFAULT_CURRENCY = "XAF"


def create_organization(
    db: Session,
    owner: User,
    name: str,
    framework: FrameworkCode,
    currency: str = DEFAULT_CURRENCY,
    is_demo: bool = False,
) -> Organization:
    org = Organization(
        name=name.strip(),
        owner_user_id=owner.id,
        framework=framework,
        currency=currency.strip().upper() or DEFAULT_CURRENCY,
        is_demo=is_demo,
    )
    db.add(org)
    db.flush()  # assign org.id

    membership = OrganizationMember(
        org_id=org.id, user_id=owner.id, role=MembershipRole.owner
    )
    db.add(membership)
    db.commit()
    db.refresh(org)

    # Demo workspaces get their framework's proper chart structure immediately so
    # the user can explore without a blank chart (OHADA = real SYSCOHADA subset;
    # IFRS = editable IAS-1 template). Session 6b.
    if is_demo:
        from app.services.account_service import seed_chart_for_organization

        seed_chart_for_organization(db, org.id)

    return org


def list_organizations_for_user(db: Session, user: User) -> list[Organization]:
    """Organizations the user is a member of, newest first."""
    rows = (
        db.query(Organization)
        .join(OrganizationMember, OrganizationMember.org_id == Organization.id)
        .filter(OrganizationMember.user_id == user.id)
        .order_by(Organization.created_at.desc())
        .all()
    )
    return rows


def get_organization_for_user(db: Session, user: User, org_id: int) -> Organization:
    """Return the org if the user is a member; raise 404 otherwise.

    404 (not 403) so the API does not reveal whether an organization exists.
    """
    org = db.get(Organization, org_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.org_id == org.id,
            OrganizationMember.user_id == user.id,
        )
        .first()
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    return org