"""Organization (workspace) service.

Logic lives here (not in the endpoint) so it is independently testable:
- creating an org always attaches the creator as an owner member,
- listing/getting is always scoped to the current user's memberships,
- the Business Profile update enforces the identity_type-driven required-
  field rules server-side (mirroring frontend/src/utils/profile.js).
"""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.accounting.identity_reference import (
    LEGAL_FORM_NOT_APPLICABLE,
    country_options,
    is_valid_country,
    is_valid_legal_form,
    legal_form_options,
)
from app.models.account import Account
from app.models.enums import (
    AccountingBasis,
    FrameworkCode,
    IdentityType,
    MembershipRole,
    OrgPurpose,
    TransactionStatus,
)
from app.models.learning import Attempt
from app.models.organization import Organization, OrganizationMember
from app.models.transaction import Transaction, TransactionLine
from app.models.user import User
from app.schemas.organization import OrganizationOut

DEFAULT_CURRENCY = "XAF"

# Stable, client-safe detail string for the archived-workspace mutation guard.
# The frontend matches on the 409 + this message to render the archived
# workspace as read-only. Reads/reports are NEVER guarded — only mutations.
ARCHIVED_WORKSPACE_DETAIL = (
    "Workspace is archived — restore it before making changes"
)


def ensure_workspace_not_archived(org: Organization | None) -> None:
    """Read-only guard for archived workspaces.

    Called by every workspace-data mutation path (draft creation, posting,
    reversal, account create/update, business-profile update — and, through
    create_draft/post, by the lesson-4 practice connector). Read and report
    endpoints deliberately do NOT call this: archived workspaces keep their
    Journal, Ledger, Trial Balance, Financial Statements and profile views.
    """
    if org is not None and org.archived_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ARCHIVED_WORKSPACE_DETAIL,
        )

# Sentinel the frontend uses for "Other" in the business-activity dropdown. When
# a user picks "Other", the free-text description REPLACES this sentinel on
# submit; a bare sentinel reaching the service is rejected (the free text is
# required when "Other" is chosen).
BUSINESS_ACTIVITY_OTHER = "OTHER"


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


def list_organizations_for_user(
    db: Session, user: User, include_archived: bool = False
) -> list[Organization]:
    """Organizations the user is a member of, newest first.

    DEFAULT excludes archived workspaces (active list). With
    include_archived=True this returns ONLY the user's ARCHIVED workspaces —
    the deliberate retrieval path behind the "Show archived workspaces"
    toggle. Both branches are membership-scoped exactly like before (a user
    never sees another user's workspaces either way).
    """
    rows = (
        db.query(Organization)
        .join(OrganizationMember, OrganizationMember.org_id == Organization.id)
        .filter(OrganizationMember.user_id == user.id)
        .filter(
            Organization.archived_at.is_not(None)
            if include_archived
            else Organization.archived_at.is_(None)
        )
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


def serialize_organization(db: Session, org: Organization) -> OrganizationOut:
    """API representation with the COMPUTED delete-eligibility flag.

    `has_protected_history` is never stored on the model — it is derived from
    real posted/reversed transactions here so the frontend can decide whether
    permanent deletion is even offered (the service re-checks it authoritatively
    inside delete_organization regardless).
    """
    return OrganizationOut.model_validate(org).model_copy(
        update={"has_protected_history": has_protected_history(db, org.id)}
    )


def has_protected_history(db: Session, org_id: int) -> bool:
    """True when the workspace has ANY posted OR reversed transaction.

    Drives the frontend's conditional permanent-delete UI and is re-checked
    (authoritatively) inside delete_organization. Reversals count too: a
    reversed pair is still accounting history, so its rows are never deleted.
    """
    exists = (
        db.query(Transaction.id)
        .filter(
            Transaction.organization_id == org_id,
            Transaction.status.in_(
                [TransactionStatus.posted, TransactionStatus.reversed]
            ),
        )
        .first()
    )
    return exists is not None


def _ensure_owner(db: Session, user: User, org_id: int) -> Organization:
    """Membership check + owner-role check for archive/restore/delete.

    - Non-members get 404 (never 403) so the API does not reveal whether the
      organization exists — same convention as get_organization_for_user.
    - Authenticated members who are NOT the owner get 403: the org's
      existence is already known to them, and archive/restore/delete are
      OWNER-ONLY actions by product rule.
    """
    org = db.get(Organization, org_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    if membership.role != MembershipRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the workspace owner can do this",
        )
    return org


def archive_organization(db: Session, user: User, org_id: int) -> Organization:
    """Archive a workspace (owner-only, idempotent, deletes NOTHING).

    Archive is the primary action: it hides the workspace from the active
    list and makes it read-only at the service layer while keeping the
    profile, accounts, drafts, posted transactions, reports and memberships
    fully intact. The owner can always restore.
    """
    org = _ensure_owner(db, user, org_id)
    if org.archived_at is None:
        org.archived_at = datetime.now(timezone.utc)
        db.commit()
    db.refresh(org)
    return org


def restore_organization(db: Session, user: User, org_id: int) -> Organization:
    """Restore an archived workspace to the active list (owner-only, idempotent)."""
    org = _ensure_owner(db, user, org_id)
    if org.archived_at is not None:
        org.archived_at = None
        db.commit()
    db.refresh(org)
    return org


def delete_organization(
    db: Session, user: User, org_id: int, confirm_name: str
) -> None:
    """Permanently delete an eligible workspace (owner-only).

    PRODUCT RULE — archive first:
    - Owner-only (members get 403; non-members 404).
    - Typed confirmation REQUIRED and validated HERE, server-side: the
      provided value must exactly match the CURRENT workspace name. The API
      never relies on a frontend-only confirmation.
    - Eligibility: ZERO posted AND ZERO reversed transactions. Any protected
      accounting history makes deletion impossible — the clear error tells
      the owner to archive instead. There is NO bypass, here or elsewhere.
    - Deletes ONLY this workspace's own dependent data, in an explicit,
      safe order (no assumed cascade behavior):
        1. draft transaction lines (drafts are the only lines possible in an
           eligible workspace — zero posted/reversed history by definition),
        2. draft transactions,
        3. accounts (all of them: with no posted/reversed lines left, no
           account is referenced by protected history),
        4. organization memberships,
        5. the organization row itself (business-profile fields live here).
    - NEVER deletes: user accounts, other organizations, learner progress,
      attempts, review records, certificate records, or public verification
      data (those are user/course-scoped, not organization-scoped — verified
      against the actual foreign keys). EXCEPTION-NOT-DELETION: attempts
      carry a NULLABLE organization_id FK; on org deletion that reference is
      cleared (set NULL) instead of deleting the attempts — history is kept,
      no dangling FK values remain.
    """
    org = _ensure_owner(db, user, org_id)

    # Server-side typed confirmation (never trust the frontend alone).
    if not confirm_name or confirm_name.strip() != org.name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Confirmation must exactly match the workspace name to "
                "permanently delete it"
            ),
        )

    # Eligibility: zero posted + zero reversed transactions. Protected
    # accounting history is immutable — archive is the only safe option.
    if has_protected_history(db, org.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This workspace has posted or reversed transactions, so it "
                "cannot be permanently deleted — archive it instead"
            ),
        )

    # --- Explicit deletion order (this workspace's data ONLY) ---------------
    # 1. Draft transaction lines. NOTE: bulk Query.delete() forbids .join()
    #    (sqlalchemy.exc.InvalidRequestError — this was the real cause of the
    #    production HTTP 500 on DELETE). A correlated subquery of this
    #    workspace's draft transaction ids is used instead, which is allowed
    #    and runs as a plain single-statement DELETE on both SQLite and
    #    PostgreSQL.
    draft_txn_ids = (
        db.query(Transaction.id)
        .filter(
            Transaction.organization_id == org.id,
            Transaction.status == TransactionStatus.draft,
        )
        .scalar_subquery()
    )
    db.query(TransactionLine).filter(
        TransactionLine.transaction_id.in_(draft_txn_ids)
    ).delete(synchronize_session=False)
    # 2. Draft transactions.
    db.query(Transaction).filter(
        Transaction.organization_id == org.id,
        Transaction.status == TransactionStatus.draft,
    ).delete(synchronize_session=False)
    # 3. Accounts — safe because eligibility guarantees no posted/reversed
    #    lines reference them (transaction_lines.account_id has NO cascade).
    db.query(Account).filter(Account.organization_id == org.id).delete(
        synchronize_session=False
    )
    # 4. Memberships.
    db.query(OrganizationMember).filter(
        OrganizationMember.org_id == org.id
    ).delete(synchronize_session=False)
    # 4b. Attempts are NEVER deleted — their nullable organization_id FK is
    #     cleared so no attempt row is orphaned with a dangling reference.
    db.query(Attempt).filter(Attempt.organization_id == org.id).update(
        {Attempt.organization_id: None}, synchronize_session=False
    )
    # 5. The organization (business-profile columns live on this row).
    db.delete(org)
    db.commit()


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
    org_purpose: OrgPurpose | None = None,
    business_activity: str | None = None,
    accounting_basis: AccountingBasis | None = None,
    company_description: str | None = None,
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

    # Archived workspaces are read-only: the business profile cannot be
    # updated (viewing it stays possible via the same GET endpoints).
    ensure_workspace_not_archived(org)

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

    # --- Session 2: purpose / activity / basis / description (all optional) ---
    # These four NEVER block saving (no required-field rules) and never feed
    # any computation — accounting_basis in particular is informational-only
    # metadata with ZERO effect on posting/ledger/statement logic (the app is
    # accrual-based; the value is stored, displayed, and nothing else).
    if org_purpose is not None:
        org.org_purpose = org_purpose.value
    if business_activity is not None:
        business_activity = business_activity.strip()
        if business_activity == BUSINESS_ACTIVITY_OTHER:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "business_activity 'OTHER' requires the free-text description "
                    "(pick Other and fill the description field)"
                ),
            )
        org.business_activity = business_activity or None
    if accounting_basis is not None:
        org.accounting_basis = accounting_basis.value
    if company_description is not None:
        company_description = company_description.strip()
        if len(company_description) > 1000:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="company_description must be 1000 characters or fewer",
            )
        org.company_description = company_description or None

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