"""Organization (workspace) service.

Logic lives here (not in the endpoint) so it is independently testable:
- creating an org always attaches the creator as an owner member,
- listing/getting is always scoped to the current user's memberships,
- the Business Profile update enforces the identity_type-driven required-
  field rules server-side (mirroring frontend/src/utils/profile.js).
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.accounting.identity_reference import (
    LEGAL_FORM_NOT_APPLICABLE,
    country_options,
    is_valid_country,
    is_valid_legal_form,
    legal_form_options,
)
from app.models.enums import FrameworkCode, IdentityType, MembershipRole
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
    identity_type: IdentityType | None = None,
    country: str | None = None,
    legal_form: str | None = None,
    framework: str | None = None,
) -> Organization:
    """Update the Business Profile of an org the user is a member of.

    PATCH semantics: only provided keys change; blank/whitespace values CLEAR
    text fields back to None. fiscal_year_start_month stays validated 1..12.

    Business Profile Part 2 — identity rules (mirrored in
    frontend/src/utils/profile.js):
    - identity_type decides which fields are required: learner (RCCM/tax not
      even shown; legal form may be the explicit NOT_APPLICABLE skip value),
      unregistered_business (RCCM/tax optional, legal form required),
      registered_business (RCCM + tax + legal form all required).
    - country: ISO 3166-1 alpha-2. OHADA orgs may ONLY use one of the 17
      member states (enforced here and by the identity-options dropdown data).
    - legal_form: framework-specific code from identity_reference.LEGAL_FORMS.
    - FRAMEWORK IS IMMUTABLE after creation: the entire seeded chart of
      accounts is framework-specific (OHADA SYSCOHADA subset / IFRS IAS-1
      template, seeded since Session 6b); switching would invalidate every
      seeded account and posted line. There is no edit path in the UI and the
      schema has no framework field in OrganizationUpdate — this explicit
      guard is belt-and-braces so a future code path cannot silently add one.
    """
    org = get_organization_for_user(db, user, org_id)

    # --- Immutable framework (see docstring) --------------------------------
    if framework is not None and framework != org.framework.value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "framework is immutable after organization creation — "
                "changing it would invalidate the seeded chart of accounts"
            ),
        )

    # --- Identity type -------------------------------------------------------
    if identity_type is not None:
        org.identity_type = identity_type.value

    # --- Country (ISO 3166-1 alpha-2; OHADA = 17 member states only) ---------
    if country is not None:
        country = country.strip().upper() or None
        if country is not None and not is_valid_country(org.framework.value, country):
            if org.framework == FrameworkCode.OHADA:
                detail = (
                    "country must be one of the 17 OHADA member states "
                    "(ISO code) for an OHADA workspace"
                )
            else:
                detail = "country must be a valid ISO 3166-1 alpha-2 code"
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
            )
        org.country = country

    # --- Legal form (framework-specific; NOT_APPLICABLE only for learners) ---
    if legal_form is not None:
        legal_form = legal_form.strip() or None
        if legal_form is not None:
            if not is_valid_legal_form(org.framework.value, legal_form):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="legal_form is not a valid form for this framework",
                )
            if (
                legal_form == LEGAL_FORM_NOT_APPLICABLE
                and org.identity_type != IdentityType.learner.value
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        "legal_form 'NOT_APPLICABLE' is only allowed for "
                        "identity_type=learner"
                    ),
                )
        org.legal_form = legal_form

    # --- Original Business Profile fields ------------------------------------
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

    # --- Identity-driven required fields (server-side mirror of profile.js) ---
    # The FINAL org state matters: a PATCH that would leave a required field
    # empty is rejected with 422 so the rules cannot be silently violated via
    # the API either. learner / legacy-unset identities add no requirements.
    if org.identity_type == IdentityType.registered_business.value:
        _missing = [
            label
            for label, value in (
                ("country", org.country),
                ("legal_form", org.legal_form),
                ("rccm_number", org.rccm_number),
                ("tax_id", org.tax_id),
            )
            if not value
        ]
        if _missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "identity_type=registered_business requires these fields: "
                    + ", ".join(_missing)
                ),
            )
    elif org.identity_type == IdentityType.unregistered_business.value:
        _missing = [
            label
            for label, value in (("country", org.country), ("legal_form", org.legal_form))
            if not value
        ]
        if _missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "identity_type=unregistered_business requires these fields: "
                    + ", ".join(_missing)
                ),
            )

    # Server-side mirror of the mandatory-step rules (frontend/src/utils/profile.js):
    # the step is complete when the BLOCKING fields exist — registered_address
    # plus fiscal_year_start_month. RCCM/tax stay optional (the learner/
    # unregistered-business paths are expressible server-side too): a workspace
    # that saves with them cleared still completes the step. Identity fields
    # are part of the profile but deliberately NOT blocking here — pre-mandate
    # orgs (migration 0011 backfill) keep their access.
    org.profile_completed = bool(org.registered_address) and bool(
        org.fiscal_year_start_month
    )

    db.commit()
    db.refresh(org)
    return org


def get_identity_options(framework: str) -> dict:
    """Dropdown data for the Business Profile form (single source of truth so
    the frontend does not duplicate ~200 country entries): only the 17 OHADA
    member states + AUSCGIE forms for OHADA, the full international list for
    IFRS."""
    return {
        "countries": country_options(framework),
        "legal_forms": legal_form_options(framework),
    }