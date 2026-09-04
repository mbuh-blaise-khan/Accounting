"""Financial-statement service (Session 10, Part A).

Generates two statements purely from posted journal lines (never manually
entered):
  * Income Statement  -> OHADA "Compte de résultat" / IFRS "Statement of
    Profit or Loss"
  * Financial Position -> OHADA "Bilan" / IFRS "Statement of Financial
    Position"

Class assignment:
  * OHADA workspaces: driven by the REAL `ohada_class_number` (1-9).
      Classes 1-5 -> Bilan (balance-sheet accounts); Classes 6-7 -> ordinary
      revenue/expense in the Compte de résultat; Class 8 (HAO - "hors
      activités ordinaires") revenue/expenses are shown as a SEPARATE
      "résultat hors activités ordinaires" section, NOT blended into the
      ordinary operating result. Class 9 (off-balance-sheet / CAGE) is
      intentionally excluded from the core statements.
  * IFRS workspaces: `ohada_class_number` is NULL, so the simplified
      `account_class` (asset/liability/equity/revenue/expense) is used.
      There is no "extraordinary" section under IFRS; the Class-8 split is
      an OHADA-only concept here.

KNOWN LIMITATION (not an oversight): this is a SIMPLIFIED presentation.
Full IAS 1 current/non-current classification of balance-sheet items is
NOT implemented — the schema has no maturity flag, so every balance-sheet
account is shown under a single "current" bucket. A future iteration can
split assets/liabilities into current vs. non-current once the model gains
a maturity dimension.

Reversed transactions: handled EXACTLY like the Trial Balance. A reversed
original + its mirror BOTH contribute their lines, so the pair nets to
zero across both statements. Drafts are never included. The date basis is
the real `posted_at` timestamp.

This is a deterministic computation — no heuristic/AI logic decides any
debit/credit outcome; balances are summed directly from the journal.
"""
from datetime import date, datetime, time, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.enums import (
    AccountClass,
    FrameworkCode,
    OrgPurpose,
    TransactionStatus,
)
from app.models.organization import Organization, OrganizationMember
from app.models.transaction import Transaction, TransactionLine
from app.models.user import User
from app.schemas.financial_statement import (
    FinancialPositionOut,
    IncomeStatementOut,
    StatementLine,
    StatementSection,
)

# A posted OR a reversed transaction both count as real history; together a
# reversed pair nets to zero. Drafts never contribute (mirrors Trial Balance).
_INCLUDE_STATUSES = [TransactionStatus.posted, TransactionStatus.reversed]

# Framework-native document names.
# OHADA workspaces: the statement names are the actual LEGAL document names
# in the OHADA zone — "Bilan (OHADA)" / "Compte de résultat (OHADA)" — and are
# NEVER translated. They read identically in both the English and the French
# UI (like "SARL" is never rendered as "LLC" elsewhere in the app). The
# disambiguating "(OHADA)" suffix is part of the name itself; ReportHeader /
# reportCsvHeader detect it and do not append the framework again.
# IFRS workspaces keep the IAS 1 English names (+ standard French
# equivalents), unchanged.
_STATEMENT_NAMES = {
    FrameworkCode.OHADA: {
        "is_en": "Compte de résultat (OHADA)",
        "is_fr": "Compte de résultat (OHADA)",
        "fs_en": "Bilan (OHADA)",
        "fs_fr": "Bilan (OHADA)",
    },
    FrameworkCode.IFRS: {
        "is_en": "Statement of Profit or Loss",
        "is_fr": "État de résultat",
        "fs_en": "Statement of Financial Position",
        "fs_fr": "Bilan",
    },
}


# Purpose-adapted terminology (presentation ONLY — never affects any amount).
# Research basis (documented, not guessed):
#  * EN: "Income and Expenditure Account" is the standard accrual statement
#    for non-profits (UK/Irish charity SORP); its bottom line is a "surplus"
#    or "deficit" of income over expenditure.
#  * FR: the French association chart of accounts (ANC) keeps the statutory
#    "compte de résultat" for associations, with the bottom line labelled
#    "excédent" / "déficit". The "compte emploi-ressources" is a DIFFERENT
#    additional analytical statement (resources vs. uses) — NOT the
#    equivalent, so it is deliberately NOT used here.
#  * government: public-sector reporting conventions are budget/cash-oriented
#    and jurisdiction-specific — no single accrual-statement name exists, so
#    government orgs KEEP the standard terminology (documented decision).
# Applies to BOTH frameworks: the purpose-specific name replaces the standard
# one (so the OHADA legal suffix is not appended for these orgs). The Bilan /
# Statement of Financial Position name is unchanged for every purpose —
# surplus/deficit is an income-statement concept only.
_INCOME_EXPENDITURE_NAMES = {
    "is_en": "Income and Expenditure Account",
    "is_fr": "Compte de résultat de l'association",
}
_INCOME_EXPENDITURE_RESULT = {
    "kind": "income_expenditure",
    "positive_en": "Surplus",
    "positive_fr": "Excédent",
    "negative_en": "Deficit",
    "negative_fr": "Déficit",
    "net_row_en": "SURPLUS/(DEFICIT)",
    "net_row_fr": "EXCÉDENT/(DÉFICIT)",
}
_PROFIT_LOSS_RESULT = {
    "kind": "profit_loss",
    "positive_en": "Profit",
    "positive_fr": "Bénéfice",
    "negative_en": "Loss",
    "negative_fr": "Perte",
    "net_row_en": "NET RESULT",
    "net_row_fr": "RÉSULTAT NET",
}


def _income_terminology(org: Organization) -> dict:
    """Income-statement terminology, adapted to the organization's purpose.

    non_profit / ngo_association -> Income & Expenditure + Surplus/Deficit.
    for_profit / government / unset -> standard Profit/Loss terminology.
    Presentation-only: changes labels, never amounts.
    """
    purpose = (getattr(org, "org_purpose", None) or "").strip()
    if purpose in (OrgPurpose.non_profit.value, OrgPurpose.ngo_association.value):
        return {"names": _INCOME_EXPENDITURE_NAMES, "result": _INCOME_EXPENDITURE_RESULT}
    return {
        "names": _STATEMENT_NAMES[
            FrameworkCode.OHADA if _is_ohada(org.framework) else FrameworkCode.IFRS
        ],
        "result": _PROFIT_LOSS_RESULT,
    }


def _ensure_org_access(db: Session, user: User, org_id: int) -> Organization:
    """Return the org if `user` is a member; raise 404 otherwise (no existence leak)."""
    org = db.get(Organization, org_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    if (
        db.query(OrganizationMember)
        .filter(OrganizationMember.org_id == org.id, OrganizationMember.user_id == user.id)
        .first()
    ) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


def _start_of(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def _end_of(d: date) -> datetime:
    return datetime.combine(d, time.max, tzinfo=timezone.utc)


def _to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (TypeError, ValueError):
        return Decimal("0")


def _account_sums(db: Session, org_id: int, after_incl, before_excl):
    """Aggregate (debit_sum, credit_sum) per account over [after_incl, before_excl).

    Either bound is optional (None = unbounded). Posted OR reversed lines
    only, on the real `posted_at` timestamp. Mirrors trial_balance_service.
    """
    q = (
        db.query(
            TransactionLine.account_id,
            func.coalesce(func.sum(TransactionLine.debit_amount), 0),
            func.coalesce(func.sum(TransactionLine.credit_amount), 0),
        )
        .join(Transaction, TransactionLine.transaction_id == Transaction.id)
        .filter(
            Transaction.organization_id == org_id,
            Transaction.status.in_(_INCLUDE_STATUSES),
            Transaction.posted_at.is_not(None),
        )
    )
    if after_incl is not None:
        q = q.filter(Transaction.posted_at >= after_incl)
    if before_excl is not None:
        q = q.filter(Transaction.posted_at < before_excl)
    return {
        account_id: (_to_decimal(d), _to_decimal(c))
        for account_id, d, c in q.group_by(TransactionLine.account_id).all()
    }


def _line(account: Account, amount: Decimal, line_type: str | None = None) -> StatementLine:
    return StatementLine(
        account_id=account.id,
        code=getattr(account, "code", None),
        name_en=account.name_en,
        name_fr=account.name_fr,
        amount=amount,
        type=line_type,
    )


def _sorted_lines(items: list[tuple[Account, Decimal, str | None]]) -> list[StatementLine]:
    """Stable ordering: OHADA by code (uncoded last), IFRS by name_en."""
    items.sort(key=lambda it: (it[0].code is None, it[0].code or "", it[0].name_en))
    return [_line(a, amt, t) for a, amt, t in items]


def _is_ohada(framework) -> bool:
    fw = framework.value if hasattr(framework, "value") else framework
    return fw == "OHADA"


def _fw_value(framework) -> str:
    return framework.value if hasattr(framework, "value") else framework


def _build_income_statement(db, org, date_from, as_of) -> IncomeStatementOut:
    ohada = _is_ohada(org.framework)
    # Presentation-only terminology adapts to the organization's purpose
    # (non_profit / ngo_association -> "Income and Expenditure Account" with
    # Surplus/Deficit); every amount below is computed exactly as before.
    terminology = _income_terminology(org)
    names = terminology["names"]
    result_labels = terminology["result"]
    currency = org.currency or "XAF"

    # Movement window = [date_from, as_of] (None bound = unbounded). When no
    # period is supplied the movement spans all history (date_from is None
    # -> everything from the beginning).
    move_after = _start_of(date_from) if date_from else None
    move_before = _end_of(as_of) if as_of else None
    sums = _account_sums(db, org.id, move_after, move_before)

    rev_items, exp_items, extra_items = [], [], []
    accounts = db.query(Account).filter(Account.organization_id == org.id).all()
    for acct in accounts:
        debit, credit = sums.get(acct.id, (Decimal("0"), Decimal("0")))
        if debit == 0 and credit == 0:
            continue
        net = credit - debit  # revenue convention (positive = net credit)
        if net == 0:
            continue  # fully-reversed pair -> net zero, not a live line

        if ohada:
            cls = acct.ohada_class_number
            if cls is None or cls == 9:  # 9 = off-balance-sheet / CAGE, excluded
                continue
            if cls == 8:  # HAO — separate section, amount stored as magnitude
                extra_items.append((acct, abs(net), "revenue" if net >= 0 else "expense"))
            elif cls == 7 and acct.account_class == AccountClass.revenue.value:
                rev_items.append((acct, net, "revenue"))
            elif cls == 6 and acct.account_class == AccountClass.expense.value:
                exp_items.append((acct, -net, "expense"))
            # classes 1-5 are balance-sheet accounts; they are not IS lines
        else:
            if acct.account_class == AccountClass.revenue.value:
                rev_items.append((acct, net, "revenue"))
            elif acct.account_class == AccountClass.expense.value:
                exp_items.append((acct, -net, "expense"))

    rev_lines = _sorted_lines(rev_items)
    rev_total = sum((l.amount for l in rev_lines), Decimal("0"))
    exp_lines = _sorted_lines(exp_items)
    exp_total = sum((l.amount for l in exp_lines), Decimal("0"))
    ordinary = rev_total - exp_total

    sections: list[StatementSection] = []
    if rev_lines:
        sections.append(StatementSection(
            key="revenue",
            label_en="Revenue",
            label_fr="Produits",
            lines=rev_lines,
            total=rev_total,
        ))
    if exp_lines:
        sections.append(StatementSection(
            key="expenses",
            label_en="Expenses",
            label_fr="Charges",
            lines=exp_lines,
            total=exp_total,
        ))

    extraordinary_total = Decimal("0")
    net_result = ordinary
    if ohada and extra_items:
        extra_lines = _sorted_lines(extra_items)
        extraordinary_total = sum((l.amount for l in extra_lines), Decimal("0"))
        sections.append(StatementSection(
            key="extraordinary",
            label_en="Extraordinary result (HAO)",
            label_fr="Résultat hors activités ordinaires",
            lines=extra_lines,
            total=extraordinary_total,
        ))
        # Recover the SIGNED contribution: extraordinary revenue adds to net,
        # extraordinary expense subtracts. Magnitudes are positive, so the
        # line's `type` field carries the side.
        extra_signed = Decimal("0")
        for l in extra_lines:
            extra_signed += l.amount if l.type == "revenue" else -l.amount
        net_result += extra_signed

    return IncomeStatementOut(
        framework=_fw_value(org.framework),
        statement_name_en=names["is_en"],
        statement_name_fr=names["is_fr"],
        statement_kind=result_labels["kind"],
        result_positive_en=result_labels["positive_en"],
        result_positive_fr=result_labels["positive_fr"],
        result_negative_en=result_labels["negative_en"],
        result_negative_fr=result_labels["negative_fr"],
        net_result_row_en=result_labels["net_row_en"],
        net_result_row_fr=result_labels["net_row_fr"],
        currency=currency,
        date_from=date_from,
        as_of=as_of,
        sections=sections,
        revenue_total=rev_total,
        expense_total=exp_total,
        extraordinary_total=extraordinary_total,
                ordinary_result=ordinary,
        net_result=net_result,
    )


def _classify_balance_sheet_account(acct: Account, ohada: bool):
    """Return 'asset' | 'liability' | 'equity' for a balance-sheet account, else None.

    Class 8 (HAO) and Class 9 (off-balance-sheet) are NOT balance-sheet
    accounts -> return None so they are skipped here.
    """
    if ohada:
        cls = acct.ohada_class_number
        if cls is None or cls in (8, 9):
            return None
        # Classes 1-5 ARE balance-sheet. The SYSCOHADA seed sets
        # `account_class` correctly for every entry (e.g. 41 Clients ->
        # asset; 40 Fournisseurs -> liability), so assignment by
        # account_class is sound. Return the raw value (str-enum compares
        # equal to its string form, and SQLAlchemy may yield either).
        return acct.account_class or None
    # IFRS: account_class is the only grouping key available.
    return acct.account_class or None


def _build_financial_position(db, org, as_of) -> FinancialPositionOut:
    ohada = _is_ohada(org.framework)
    names = _STATEMENT_NAMES[FrameworkCode.OHADA if ohada else FrameworkCode.IFRS]
    currency = org.currency or "XAF"

    close_before = _end_of(as_of) if as_of else None
    sums = _account_sums(db, org.id, None, close_before)

    ast_items, lia_items, eq_items = [], [], []
    accounts = db.query(Account).filter(Account.organization_id == org.id).all()
    for acct in accounts:
        debit, credit = sums.get(acct.id, (Decimal("0"), Decimal("0")))
        if debit == 0 and credit == 0:
            continue
        # Net signed balance: debit side positive, credit side negative.
        net_signed = debit - credit
        kind = _classify_balance_sheet_account(acct, ohada)
        if kind is None:
            continue
        if net_signed == 0:
            continue  # fully-reversed pair -> net zero, not a live line
        # SIGNED contribution on the account's own side (root-cause fix for
        # the "Unbalanced" warning on balanced ledgers): an ASSET with a net
        # CREDIT balance (bank overdraft, sloppy/demo post) and a LIABILITY
        # or EQUITY account with a net DEBIT balance must count NEGATIVELY in
        # their section. Using abs() here (as the code once did) silently
        # flips such balances to a positive magnitude, doubling their
        # contribution and breaking
        #     assets = liabilities + equity + net_result
        # even when the raw ledger (debits == credits) is perfectly balanced.
        if kind == "asset":
            ast_items.append((acct, net_signed, None))
        elif kind == "liability":
            lia_items.append((acct, -net_signed, None))
        elif kind == "equity":
            eq_items.append((acct, -net_signed, None))

    assets = sum((a for _, a, _ in ast_items), Decimal("0"))
    liabilities = sum((a for _, a, _ in lia_items), Decimal("0"))
    equity = sum((a for _, a, _ in eq_items), Decimal("0"))

    sections: list[StatementSection] = []
    if ast_items:
        sections.append(StatementSection(
            key="assets", label_en="Assets", label_fr="Actif",
            lines=_sorted_lines(ast_items), total=assets,
        ))
    if lia_items:
        sections.append(StatementSection(
            key="liabilities", label_en="Liabilities", label_fr="Dettes",
            lines=_sorted_lines(lia_items), total=liabilities,
        ))
    if eq_items:
        sections.append(StatementSection(
            key="equity",
            label_en="Equity",
            label_fr="Capitaux propres",
            lines=_sorted_lines(eq_items),
            total=equity,
        ))

    return FinancialPositionOut(
        framework=_fw_value(org.framework),
        statement_name_en=names["fs_en"],
        statement_name_fr=names["fs_fr"],
        currency=currency,
        as_of=as_of,
        sections=sections,
        assets=assets,
        liabilities=liabilities,
        equity=equity,
        balanced=(assets == liabilities + equity),
    )


def get_income_statement(
    db: Session,
    user: User,
    org_id: int,
    date_from: date | None = None,
    as_of: date | None = None,
) -> IncomeStatementOut:
    """Compte de résultat / Statement of Profit or Loss for one org over [date_from, as_of].

    Both bounds optional (None = unbounded on that side). The movement
    covers ordinary revenue (class 7 / IFRS revenue) minus ordinary expenses
    (class 6 / IFRS expense), plus a SEPARATE HAO section for OHADA class 8.
    `ordinary_result` excludes HAO; `net_result` adds the extraordinary
    (HAO) contribution back.
    """
    org = _ensure_org_access(db, user, org_id)
    return _build_income_statement(db, org, date_from, as_of)


def get_financial_position(
    db: Session,
    user: User,
    org_id: int,
    as_of: date | None = None,
) -> FinancialPositionOut:
    """Bilan / Statement of Financial Position as of `as_of` (None = all history).

    Uses closing balances (everything up to `as_of`). A reversed pair and
    its original BOTH contribute their lines, so the pair nets to zero
    across the statement — exactly like the Trial Balance. Drafts are
    excluded.
    """
    org = _ensure_org_access(db, user, org_id)
    return _build_financial_position(db, org, as_of)
