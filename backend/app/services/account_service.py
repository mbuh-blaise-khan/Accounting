"""Chart of accounts service.

Scoped to the user's memberships (an org's chart is only visible/editable by
its members). Custom-account creation enforces code uniqueness within the
org+framework pair. Deactivation enforces the "no posted transactions" rule.

The seeded chart data lives in app/accounting/:
- OHADA workspaces get the REAL official SYSCOHADA structure (2017 révisé) from
  docs/ohada-ifrs-source-reference.md (a representative subset, all 9 classes,
  hierarchical via parent_account_id and ohada_class_number).
- IFRS workspaces get an editable IAS-1-aligned STARTING TEMPLATE (IFRS has no
  mandated chart of accounts; see the reference doc).
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.accounting.ifrs_template import IFRS_TEMPLATE
from app.accounting.ohada_chart import OHADA_CHART
from app.models.account import Account
from app.models.enums import FrameworkCode, NormalBalance, TransactionStatus
from app.models.organization import Organization, OrganizationMember
from app.models.transaction import Transaction, TransactionLine
from app.models.user import User


def _ensure_org_access(db: Session, user: User, org_id: int) -> Organization:
    """Return the org if the user is a member; raise 404 otherwise.

    404 (not 403) so the API does not reveal whether an organization exists —
    same convention as organization_service.
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
    return org


def _get_owned_account(db: Session, user: User, org_id: int, account_id: int) -> Account:
    """Return an account that belongs to an org the user is a member of."""
    _ensure_org_access(db, user, org_id)
    account = db.get(Account, account_id)
    if account is None or account.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    return account


def list_accounts(db: Session, user: User, org_id: int) -> list[Account]:
    """All accounts in an org's chart (active + inactive), by code."""
    _ensure_org_access(db, user, org_id)
    return (
        db.query(Account)
        .filter(Account.organization_id == org_id)
        .order_by(Account.code)
        .all()
    )


def create_custom_account(
    db: Session,
    user: User,
    organization_id: int,
    framework: FrameworkCode,
    code: str | None = None,
    name_en: str,
    name_fr: str,
    account_class,
    normal_balance: NormalBalance,
    parent_account_id: int | None = None,
    description: str = "",
    ohada_class_number: int | None = None,
) -> Account:
    """Create a user-defined account, enforcing org scoping + code uniqueness.

    Part B: only OHADA accounts carry a code. OHADA REQUIRES a code (real
    SYSCOHADA numbering); IFRS accounts never store one — any supplied code is
    ignored and the `code` column is stored NULL (IFRS has no mandated chart of
    accounts / numbering).
    """
    org = _ensure_org_access(db, user, organization_id)

    # A custom account's framework must match the org's chosen framework.
    if FrameworkCode(framework) != FrameworkCode(org.framework):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account framework must match the organization's framework",
        )

    is_ohada = FrameworkCode(framework) == FrameworkCode.OHADA
    code_value = code.strip() if code is not None else None
    if is_ohada and not code_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="An OHADA account requires a code",
        )
    if not is_ohada:
        code_value = None  # IFRS accounts never store a code

    if code_value is not None:
        existing = (
            db.query(Account)
            .filter(
                Account.organization_id == organization_id,
                Account.framework == framework,
                Account.code == code_value,
            )
            .first()
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this code already exists for this framework",
            )

    if parent_account_id is not None:
        parent = db.get(Account, parent_account_id)
        if parent is None or parent.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent account not found in this organization",
            )

    account = Account(
        organization_id=organization_id,
        framework=framework,
        code=code_value,
        name_en=name_en.strip(),
        name_fr=name_fr.strip(),
        account_class=account_class,
        parent_account_id=parent_account_id,
        normal_balance=normal_balance,
        is_system_default=False,
        active=True,
        description=description.strip(),
        ohada_class_number=ohada_class_number,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def has_posted_transactions(db: Session, account_id: int) -> bool:
    """Return True if the account appears in a transaction that has been posted.

    A draft transaction does not count — the account can still be deactivated
    while only referenced by drafts. Once posted (or reversed), the account has
    accounting history and must not be deactivated.
    """
    line = (
        db.query(TransactionLine)
        .join(Transaction, Transaction.id == TransactionLine.transaction_id)
        .filter(
            TransactionLine.account_id == account_id,
            Transaction.status != TransactionStatus.draft,
        )
        .first()
    )
    return line is not None


def update_account(
    db: Session,
    user: User,
    org_id: int,
    account_id: int,
    name_en: str | None = None,
    name_fr: str | None = None,
    active: bool | None = None,
) -> Account:
    """Edit plain-language names and/or toggle active for an org's account."""
    account = _get_owned_account(db, user, org_id, account_id)

    if active is not None and active is False and account.active:
        # Rule: never deactivate an account with existing posted transactions.
        if has_posted_transactions(db, account.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot deactivate an account that has posted transactions",
            )

    if name_en is not None:
        account.name_en = name_en.strip()
    if name_fr is not None:
        account.name_fr = name_fr.strip()
    if active is not None:
        account.active = active

    db.add(account)
    db.commit()
    db.refresh(account)
    return account


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def _ohada_class_number(code: str) -> int | None:
    """First digit of an OHADA code is its class (1-9); None otherwise."""
    if code and code[0].isdigit():
        return int(code[0])
    return None


def _insert_seed_entries(
    db: Session, org: Organization, fw: FrameworkCode, entries: list[dict],
    ohada: bool = True,
) -> list[Account]:
    """Insert seed entries (idempotent), resolving parent codes within the org.

    Entries must be ordered parents-before-children; parents are resolved to
    existing rows by code (either just-created or pre-existing). `ohada` marks
    whether these entries carry a real OHADA class number and use code-keyed
    idempotency.

    Part B: IFRS accounts have NO codes. The IFRS template is seeded with
    `code=NULL` (the shared `accounts.code` column is kept for OHADA), keyed for
    idempotency by `name_en` (unique in the template), and has no parents.
    """
    created: list[Account] = []
    existing: dict[str, int] = {}
    for row in db.query(Account).filter(
        Account.organization_id == org.id, Account.framework == fw
    ):
        if ohada:
            if row.code is not None:
                existing[row.code] = row.id
        else:
            existing[row.name_en] = row.id

    for item in entries:
        key = item["code"] if ohada else item["name_en"]
        existing_id = existing.get(key)
        if existing_id is not None:
            continue  # idempotent: already seeded
        parent_id = None
        if ohada and item.get("parent"):
            parent_id = existing.get(item["parent"])
        account = Account(
            organization_id=org.id,
            framework=fw,
            code=item.get("code") if ohada else None,
            name_en=item["name_en"],
            name_fr=item["name_fr"],
            account_class=item["account_class"],
            parent_account_id=parent_id,
            normal_balance=item["normal_balance"],
            is_system_default=True,
            active=True,
            description=item.get("description", ""),
            ohada_class_number=(
                _ohada_class_number(item["code"]) if ohada else None
            ),
        )
        db.add(account)
        db.flush()  # assign account.id so children can link via parent id
        existing[key] = account.id
        created.append(account)

    db.commit()
    return created


def seed_ohada_chart(db: Session, org: Organization, fw: FrameworkCode) -> list[Account]:
    """Seed the real official SYSCOHADA chart (representative subset).

    Real data sourced from OHADA's 2017 révisé Acte Uniforme (see
    app/accounting/ohada_chart.py). Seeded coverage is representative — this is
    not the full ~900-line official list.
    """
    return _insert_seed_entries(db, org, fw, OHADA_CHART)


def seed_ifrs_template(db: Session, org: Organization, fw: FrameworkCode) -> list[Account]:
    """Seed the editable IAS-1-aligned IFRS starting template.

    IFRS has NO mandated chart of accounts (see the reference doc), so this is
    a flexible template the business is expected to adapt — not a fixed
    official list. ohada_class_number stays NULL.
    """
    return _insert_seed_entries(db, org, fw, IFRS_TEMPLATE, ohada=False)


def seed_chart_for_organization(
    db: Session, organization_id: int, framework: FrameworkCode | None = None
) -> list[Account]:
    """Seed the correct chart structure for an organization by its framework."""
    org = db.get(Organization, organization_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    fw = framework if framework is not None else FrameworkCode(org.framework)
    if fw == FrameworkCode.IFRS:
        return seed_ifrs_template(db, org, fw)
    return seed_ohada_chart(db, org, fw)