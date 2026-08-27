"""Trial Balance service (Session 9).

For an organization and optional period [date_from, as_of] we compute, for
EVERY account in one pass:
- opening balance  = net of all included lines posted BEFORE the period start
                     (0 when no `date_from` is given — "all time"),
- movement         = total debit and credit WITHIN the period,
- closing balance  = opening + net movement, i.e. everything up to `as_of`.

The three figures come from ONE computation so the frontend can render the
2-column (closing only), 4-column (movement + closing) or 6-column (opening +
movement + closing) views from the same payload without a new API call.

Included lines: transactions with status POSTED **or REVERSED** (a reversed
original is still real history; together with its mirror it nets to zero).
Drafts are never included. Consistent with Journal/Ledger, the date basis is
the real `posted_at` timestamp.

Zero-activity accounts are OMITTED rather than shown with zeros (documented
decision): the report stays short for beginners; their absence is exactly
equivalent to displaying zeros.
"""
from datetime import date, datetime, time, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func

from app.models.account import Account
from app.models.enums import TransactionStatus
from app.models.organization import Organization, OrganizationMember
from app.models.transaction import Transaction, TransactionLine
from app.models.user import User
from app.schemas.trial_balance import (
    TrialBalanceOut,
    TrialBalanceRowOut,
    TrialBalanceTotalsOut,
)

_INCLUDED_STATUSES = [TransactionStatus.posted, TransactionStatus.reversed]


def _ensure_org_access(db, user: User, org_id: int) -> Organization:
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
    except Exception:  # noqa: BLE001 - never let a bad row crash the report
        return Decimal(0)


def _sums_by_account(db, org_id: int, after_incl, before_excl):
    """Aggregate debit/credit sums per account over [after_incl, before_excl)
    (either bound optional). Same filters as Journal/Ledger: org-scoped,
    posted + reversed only, real posted_at basis. Returns
    {account_id: (debit_sum, credit_sum)}."""
    q = (
        db.query(
            TransactionLine.account_id,
            func.coalesce(func.sum(TransactionLine.debit_amount), 0),
            func.coalesce(func.sum(TransactionLine.credit_amount), 0),
        )
        .join(Transaction, Transaction.id == TransactionLine.transaction_id)
        .filter(
            Transaction.organization_id == org_id,
            Transaction.status.in_(_INCLUDED_STATUSES),
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


def _place(net: Decimal) -> tuple[Decimal, Decimal]:
    """Put a signed net where a trial balance shows it: net debit → Debit
    column, net credit → Credit column (both zero when flat). This follows the
    classic convention — placement by where the balance ACTUALLY sits, not by
    the account's normal_balance (an overdrawn cash account shows a CREDIT
    balance in the trial balance)."""
    if net > 0:
        return net, Decimal("0")
    if net < 0:
        return Decimal("0"), -net
    return Decimal("0"), Decimal("0")


def get_trial_balance(
    db,
    user: User,
    org_id: int,
    date_as_of: date | None = None,
    date_from: date | None = None,
    columns: int = 2,
) -> TrialBalanceOut:
    """Compute the trial balance for one org over [date_from, date_as_of].

    Every response carries opening/movement/closing regardless of the chosen
    view so the frontend can switch between 2/4/6 columns without refetching.
    closing = opening + movement holds by construction for every account.
    """
    _ensure_org_access(db, user, org_id)

    # Closing window: everything up to the END of the as_of day (unbounded
    # when as_of is omitted). Opening window: strictly BEFORE the period
    # start. Movement = what happens between the two windows.
    close_sums = _sums_by_account(db, org_id, None, _end_of(date_as_of) if date_as_of else None)
    if date_from is not None:
        opening_sums = _sums_by_account(db, org_id, None, _start_of(date_from))
        move_sums = _sums_by_account(db, org_id, _start_of(date_from), _end_of(date_as_of) if date_as_of else None)
    else:
        # No period start: all history is "movement", opening is zero.
        opening_sums = {}
        move_sums = close_sums

    rows_out: list[TrialBalanceRowOut] = []
    accounts = db.query(Account).filter(Account.organization_id == org_id).all()
    totals = {k: Decimal("0") for k in (
        "opening_debit", "opening_credit", "movement_debit",
        "movement_credit", "closing_debit", "closing_credit",
    )}

    for account in accounts:
        od_raw_d, od_raw_c = opening_sums.get(account.id, (Decimal("0"), Decimal("0")))
        mv_d, mv_c = move_sums.get(account.id, (Decimal("0"), Decimal("0")))
        cl_d, cl_c = close_sums.get(account.id, (Decimal("0"), Decimal("0")))

        # Self-check of the one-computation invariant (raw net convention):
        # closing must equal opening + movement.
        assert cl_d - cl_c == (od_raw_d - od_raw_c) + (mv_d - mv_c), (
            f"trial balance internal inconsistency for account {account.id}"
        )

        # Opening & closing are shown as NET balances on their side (classic
        # trial balance); MOVEMENT columns show GROSS period debit/credit
        # activity, matching real software (QuickBooks/Sage) — every
        # transaction contributes its full debit and its full credit, so the
        # gross movement TOTALS also always balance.
        od, oc = _place(od_raw_d - od_raw_c)
        md, mc = mv_d, mv_c
        cd, cc = _place(cl_d - cl_c)

        zero = Decimal("0")
        if (od, oc, md, mc, cd, cc) == (zero, zero, zero, zero, zero, zero):
            continue  # zero-activity account: omitted (documented decision)

        rows_out.append(
            TrialBalanceRowOut(
                account_id=account.id,
                code=account.code,
                name_en=account.name_en,
                name_fr=account.name_fr,
                normal_balance=getattr(
                    account.normal_balance, "value", account.normal_balance
                ) or "debit",
                opening_debit=od,
                opening_credit=oc,
                movement_debit=md,
                movement_credit=mc,
                closing_debit=cd,
                closing_credit=cc,
            )
        )
        totals["opening_debit"] += od
        totals["opening_credit"] += oc
        totals["movement_debit"] += md
        totals["movement_credit"] += mc
        totals["closing_debit"] += cd
        totals["closing_credit"] += cc

    # OHADA: ascending account code first (uncoded last); IFRS falls back to
    # the English name. One stable order for every view.
    rows_out.sort(key=lambda r: (r.code is None, r.code or "", r.name_en))

    return TrialBalanceOut(
        date_from=date_from,
        as_of=date_as_of,
        columns=columns,
        rows=rows_out,
        totals=TrialBalanceTotalsOut(**totals),
        balanced=totals["closing_debit"] == totals["closing_credit"],
    )
