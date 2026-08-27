"""Journal and Cash Book service (Session 7).

A read-only view over POSTED transactions and their lines. The Journal renders
every line of every posted transaction (filterable by date range, account and
reference); the Cash Book is the same view filtered to cash/bank accounts only.

Framework-aware:
- OHADA workspaces carry real SYSCOHADA account numbers (shown in the Journal).
- IFRS accounts have no code (Part B): `account_code` is NULL, and the frontend
  omits the account-number column. Cash/bank detection for IFRS falls back to a
  keyword match on the account name, since there are no numbered classes.

The row date is the transaction's real `posted_at` (Part C), the first column
wherever a posted transaction appears.
"""
from datetime import date, datetime, time, timezone
from decimal import Decimal
import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.account import Account
from app.models.enums import TransactionStatus
from app.models.organization import Organization, OrganizationMember
from app.models.transaction import Transaction, TransactionLine
from app.models.user import User
from app.schemas.journal import JournalEntryOut

# Cash / bank keyword fallback for IFRS (which has no numbered classes)
# and for legacy OHADA rows that lack an ohada_class_number.
_CASH_KEYWORDS = (
    "cash", "bank", "banque", "caisse", "tresorerie", "trésorerie", "treasury",
    "espèces", "caisses",
)


def _ensure_org_access(db: Session, user: User, org_id: int) -> Organization:
    """Return the org if the user is a member; raise 404 otherwise."""
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


def _start_of(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def _end_of(d: date) -> datetime:
    return datetime.combine(d, time.max, tzinfo=timezone.utc)


def _to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal(0)


def _cashbook_account_type(account: Account, framework: str) -> str | None:
    """Classify a treasury account for the Cash Book as ``cash`` or ``bank``.

    This deliberately distinguishes physical cash from bank balances. For OHADA,
    57 is Caisse and 52/56 are bank-related classes. IFRS has no mandated account
    numbering, so names are used, with bank keywords taking precedence over cash
    keywords (e.g. "cash at bank" is bank, not physical cash).
    """
    if not account:
        return None
    code = (account.code or "").strip()
    if framework == "OHADA":
        if code.startswith("57"):
            return "cash"
        if code.startswith("52") or code.startswith("56"):
            return "bank"
    text = f"{account.name_en or ''} {account.name_fr or ''}".lower()
    bank_words = ("bank", "banque", "overdraft", "découvert")
    cash_words = ("cash", "caisse", "espèces", "especes", "petty cash")
    if any(word in text for word in bank_words):
        return "bank"
    if any(word in text for word in cash_words):
        return "cash"
    return None


def _is_cash_bank(account: Account, framework: str) -> bool:
    """Backward-compatible combined treasury predicate."""
    return _cashbook_account_type(account, framework) is not None


def parse_reference_query(reference):
    """Parse a Journal reference search into a transaction id (Part A contract).

    The Reference column shows "TX-{id:04d}", so a reference search matches
    THAT field — not the description. Pure helper so the contract is
    unit-testable without a database:

    - ``"TX-0012"`` / ``"tx_0012"`` / ``"TX 12"`` / ``"0012"`` / ``"12"``
      all resolve to transaction id 12;
    - any query with no digits at all can never match a reference and yields
      ``None`` (callers must return zero rows for it).

    Returns the parsed int id, or None when no id token is present.
    """
    if reference is None:
        return None
    m = re.search(r"(?:TX[-_ ]?)?(\d+)", reference.strip(), re.IGNORECASE)
    return int(m.group(1)) if m else None


def list_journal_entries(
    db: Session,
    user: User,
    org_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    account_id: int | None = None,
    reference: str | None = None,
    cashbook_only: bool = False,
) -> list[JournalEntryOut]:
    """Posted transaction lines, oldest-posted first, filterable.

    Always restricted to the user's own org and to POSTED transactions — drafts
    never appear in the Journal/Cash Book.
    """
    org = _ensure_org_access(db, user, org_id)
    framework = getattr(org.framework, "value", org.framework) or ""

    q = (
        db.query(TransactionLine)
        .join(Transaction, Transaction.id == TransactionLine.transaction_id)
        .options(
            joinedload(TransactionLine.account),
            joinedload(TransactionLine.transaction),
        )
        .filter(
            Transaction.organization_id == org_id,
            # Posted AND reversed transactions are immutable and appear in the
            # journal; drafts never do. Keeping a reversed original visible
            # alongside its reversal shows the cancelling pair (net-zero).
            Transaction.status.in_(
                [TransactionStatus.posted, TransactionStatus.reversed]
            ),
            Transaction.posted_at.is_not(None),
        )
    )
    if date_from is not None:
        q = q.filter(Transaction.posted_at >= _start_of(date_from))
    if date_to is not None:
        q = q.filter(Transaction.posted_at <= _end_of(date_to))
    if account_id is not None:
        q = q.filter(TransactionLine.account_id == account_id)
    if reference and reference.strip():
        # The Reference column shows "TX-{id:04d}". A reference search must
        # match THAT field, not the description (Part A fix). Parse an id
        # token from the query (pure helper, unit-tested): "TX-0012" / "0012"
        # / "12" all resolve to transaction id 12. A query with no digits
        # (e.g. a word that only appears in a description) can never match a
        # reference -> no rows.
        parsed = parse_reference_query(reference)
        if parsed is None:
            q = q.filter(Transaction.id == -1)
        else:
            q = q.filter(Transaction.id == parsed)

    rows = (
        q.order_by(
            Transaction.posted_at.asc(),
            Transaction.id.asc(),
            TransactionLine.id.asc(),
        )
        .all()
    )

    out: list[JournalEntryOut] = []
    for line in rows:
        cashbook_type = _cashbook_account_type(line.account, framework)
        if cashbook_only and (cashbook_type is None):
            continue
        txn = line.transaction
        acct = line.account
        out.append(
            JournalEntryOut(
                id=line.id,
                transaction_id=txn.id,
                date=txn.posted_at,
                reference=f"TX-{txn.id:04d}",
                description=txn.description,
                account_id=acct.id if acct else line.account_id,
                account_code=acct.code if acct else None,
                account_name_en=acct.name_en if acct else None,
                account_name_fr=acct.name_fr if acct else None,
                debit=_to_decimal(line.debit_amount),
                credit=_to_decimal(line.credit_amount),
                narration=line.narration,
                source="manual",
                status=txn.status.value,
                created_by=txn.created_by,
                created_at=txn.created_at,
                cashbook_type=cashbook_type,
            )
        )
    return out


def list_cash_book(
    db: Session,
    user: User,
    org_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    account_id: int | None = None,
    reference: str | None = None,
    cashbook_type: str = "double",
) -> list[JournalEntryOut]:
    """Return single-column cash only, or double-column cash and bank rows."""
    if cashbook_type not in {"single", "double"}:
        raise HTTPException(status_code=422, detail="type must be 'single' or 'double'")
    rows = list_journal_entries(
        db, user, org_id, date_from, date_to, account_id, reference,
        cashbook_only=True,
    )
    return [row for row in rows if row.cashbook_type == "cash"] if cashbook_type == "single" else rows