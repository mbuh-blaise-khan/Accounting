"""Chart of accounts service.

Scoped to the user's memberships (an org's chart is only visible/editable by
its members). Custom-account creation enforces code uniqueness within the
org+framework pair. Deactivation enforces the "no posted transactions" rule
(placeholder until Session 6 adds transactions).
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.enums import AccountClass, FrameworkCode, NormalBalance
from app.models.organization import Organization, OrganizationMember
from app.models.user import User

# ---------------------------------------------------------------------------
# ILLUSTRATIVE / DEMO chart of accounts
# ---------------------------------------------------------------------------
# These account definitions are DEMO DATA ONLY. They are deliberately small and
# plain so a non-accountant can understand them, and they are NOT derived from
# any official OHADA or IFRS classification (never fabricate an official chart).
#
# >>> Replace with a reviewed / licensed official chart before any real
# >>> production or compliance use.
# ---------------------------------------------------------------------------

# The same illustrative set is used for every framework label; the `framework`
# column tags which context the rows belong to. normal_balance is inferred from
# the account class here because that is deterministic (no AI decision).
_CLASS_BALANCE: dict[str, str] = {
    AccountClass.asset.value: NormalBalance.debit.value,
    AccountClass.liability.value: NormalBalance.credit.value,
    AccountClass.equity.value: NormalBalance.credit.value,
    AccountClass.revenue.value: NormalBalance.credit.value,
    AccountClass.expense.value: NormalBalance.debit.value,
}


def _ac(code: str, name_en: str, name_fr: str, account_class: AccountClass,
        description: str = "") -> dict:
    """Build one illustrative account row, deriving its normal balance."""
    return {
        "code": code,
        "name_en": name_en,
        "name_fr": name_fr,
        "account_class": account_class.value,
        "normal_balance": _CLASS_BALANCE[account_class.value],
        "description": description,
    }


# ILLUSTRATIVE DEMO DATA — replace with a reviewed/licensed official chart
# before any real production or compliance use.
ILLUSTRATIVE_CHART: list[dict] = [
    _ac("1000", "Cash", "Caisse", AccountClass.asset,
        "Physical money on hand."),
    _ac("1100", "Bank", "Banque", AccountClass.asset,
        "Money held in a bank account."),
    _ac("1200", "Accounts receivable", "Clients (créances)", AccountClass.asset,
        "Money customers owe us."),
    _ac("1300", "Inventory", "Stock de marchandises", AccountClass.asset,
        "Goods we hold to sell."),
    _ac("1400", "Equipment", "Équipement", AccountClass.asset,
        "Machines, computers and tools used in the business."),
    _ac("2000", "Accounts payable", "Fournisseurs (dettes)", AccountClass.liability,
        "Money we owe to suppliers."),
    _ac("2100", "Loans payable", "Emprunts", AccountClass.liability,
        "Money we owe on a loan."),
    _ac("3000", "Owner\u2019s capital", "Capital", AccountClass.equity,
        "Money the owner put into the business."),
    _ac("3100", "Retained earnings", "Réserves", AccountClass.equity,
        "Profits kept in the business."),
    _ac("4000", "Sales revenue", "Ventes", AccountClass.revenue,
        "Money from selling goods."),
    _ac("4100", "Service revenue", "Prestations de services", AccountClass.revenue,
        "Money from providing services."),
    _ac("5000", "Purchases", "Achats", AccountClass.expense,
        "Cost of goods bought to resell."),
    _ac("5100", "Rent expense", "Loyer", AccountClass.expense,
        "Cost of renting the premises."),
    _ac("5200", "Salaries expense", "Salaires", AccountClass.expense,
        "Wages and salaries paid to staff."),
    _ac("5300", "Utilities expense", "Factures d\u2019énergie", AccountClass.expense,
        "Electricity, water and internet bills."),
    _ac("5400", "Advertising expense", "Publicité", AccountClass.expense,
        "Cost of promoting the business."),
    _ac("5500", "Supplies expense", "Fournitures", AccountClass.expense,
        "Cost of office supplies."),
    _ac("5600", "Other expenses", "Autres charges", AccountClass.expense,
        "Miscellaneous business expenses."),
]

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
    """All accounts in an org's chart (active + inactive), class then code."""
    _ensure_org_access(db, user, org_id)
    return (
        db.query(Account)
        .filter(Account.organization_id == org_id)
        .order_by(Account.account_class, Account.code)
        .all()
    )


def create_custom_account(
    db: Session,
    user: User,
    organization_id: int,
    framework: FrameworkCode,
    code: str,
    name_en: str,
    name_fr: str,
    account_class: AccountClass,
    normal_balance: NormalBalance,
    parent_account_id: int | None = None,
    description: str = "",
) -> Account:
    """Create a user-defined account, enforcing org scoping + code uniqueness."""
    org = _ensure_org_access(db, user, organization_id)

    # A custom account's framework must match the org's chosen framework.
    if FrameworkCode(framework) != FrameworkCode(org.framework):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account framework must match the organization's framework",
        )

    existing = (
        db.query(Account)
        .filter(
            Account.organization_id == organization_id,
            Account.framework == framework,
            Account.code == code.strip(),
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
        code=code.strip(),
        name_en=name_en.strip(),
        name_fr=name_fr.strip(),
        account_class=account_class,
        parent_account_id=parent_account_id,
        normal_balance=normal_balance,
        is_system_default=False,
        active=True,
        description=description.strip(),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def has_posted_transactions(db: Session, account_id: int) -> bool:
    """Return True if the account appears in any posted transaction line.

    PLACEHOLDER (Session 5): the `transactions` / `transaction_lines` tables
    are built in Session 6, so this always returns False for now. When those
    tables exist, reimplement by joining transaction_lines -> transactions where
    status == 'posted'. The PATCH handler below already rejects deactivation
    when this returns True, so the rule is enforced as soon as data exists.

    TODO(Session 6): real implementation after transactions table is added.
    """
    return False


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


def seed_illustrative_chart(
    db: Session, organization_id: int, framework: FrameworkCode | None = None
) -> list[Account]:
    """Seed the ILLUSTRATIVE demo chart for an organization.

    ILLUSTRATIVE DEMO DATA — replace with a reviewed/licensed official chart
    before any real production or compliance use. Idempotent: existing accounts
    by (org, framework, code) are left untouched.
    """
    org = db.get(Organization, organization_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    fw = framework if framework is not None else FrameworkCode(org.framework)

    created: list[Account] = []
    for item in ILLUSTRATIVE_CHART:
        existing = (
            db.query(Account)
            .filter(
                Account.organization_id == org.id,
                Account.framework == fw,
                Account.code == item["code"],
            )
            .first()
        )
        if existing is not None:
            continue  # idempotent
        account = Account(
            organization_id=org.id,
            framework=fw,
            code=item["code"],
            name_en=item["name_en"],
            name_fr=item["name_fr"],
            account_class=item["account_class"],
            normal_balance=item["normal_balance"],
            is_system_default=True,
            active=True,
            description=item["description"],
        )
        db.add(account)
        created.append(account)

    db.commit()
    return created
