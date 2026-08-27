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

    # EVERY new workspace is seeded with its framework's proper chart structure
    # immediately, demo or not (OHADA = the real representative SYSCOHADA subset;
    # IFRS = the editable IAS-1 template). Session 6b gated this to is_demo=True;
    # that was a wrong design choice for OHADA, whose SYSCOHADA numbering is a
    # legally standardized national system every real business starts from — a
    # blank non-demo chart made autocomplete and transaction posting impossible.
    # IFRS is handled the same way (its editable template is a starting point).
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


def update_business_profile(
    db: Session,
    user: User,
    org_id: int,
    registered_address: str | None = None,
    rccm_number: str | None = None,
    tax_id: str | None = None,
    fiscal_year_start_month: int | None = None,
) -> Organization:
    """Update the optional Business Profile of an org the user is a member of.

    All fields are optional (PATCH semantics: only provided keys change). The
    registration/address/tax fields were intentionally never required, so a
    blank/whitespace value CLEARS them back to None rather than storing empty
    strings. fiscal_year_start_month is validated 1..12 and defaults to 1
    (January / calendar year) when unset — it drives period math, not display.
    """
    org = get_organization_for_user(db, user, org_id)

    if registered_address is not None:
        org.registered_address = registered_address.strip() or None
    if rccm_number is not None:
        org.rccm_number = rccm_number.strip() or None
    if tax_id is not None:
        org.tax_id = tax_id.strip() or None
    if fiscal_year_start_month is not None:
        if not 1 <= fiscal_year_start_month <= 12:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="fiscal_year_start_month must be between 1 and 12",
            )
        org.fiscal_year_start_month = fiscal_year_start_month

    db.commit()
    db.refresh(org)
    return org