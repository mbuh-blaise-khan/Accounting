"""Backfill/repair charts of accounts so EVERY workspace has its framework chart.

Session 8 policy fix: a workspace's chart is no longer gated to is_demo=True —
every new OHADA workspace starts with the real representative SYSCOHADA subset
and every new IFRS workspace starts with the 27-entry IAS-1 template (both
seeded automatically by organization_service.create_organization).

WHY THIS SCRIPT STILL EXISTS
----------------------------
1. BACKFILL: any org created BEFORE the fix lacks the canonical chart — either
   stale demo orgs holding the legacy illustrative chart, or real non-demo orgs
   that were created EMPTY because the old code only seeded demos. This script
   repairs them in place without recreating the org.
2. IFRS Part-B repair: legacy IFRS accounts that still carry CODES are
   corrected to code=NULL (IFRS has no mandated numbering).

It runs against ALL organizations by default (every org should have its
framework's chart). `--demo-only` restricts to demo orgs on request.

Usage (from backend/ with the venv active):

    .venv/Scripts/python.exe -m scripts.reseed_charts              # backfill all orgs
    .venv/Scripts/python.exe -m scripts.reseed_charts --org 4      # single org
    .venv/Scripts/python.exe -m scripts.reseed_charts --dry-run    # preview only
    .venv/Scripts/python.exe -m scripts.reseed_charts --demo-only  # only demo orgs

Idempotent: re-running is safe and reaches the same end state.
"""
import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.accounting.ifrs_template import IFRS_TEMPLATE  # noqa: E402
from app.accounting.ohada_chart import OHADA_CHART  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.models.account import Account  # noqa: E402
from app.models.enums import FrameworkCode  # noqa: E402
from app.models.organization import Organization  # noqa: E402
from app.models.transaction import Transaction, TransactionLine  # noqa: E402
from app.services.account_service import (  # noqa: E402
    seed_ifrs_template,
    seed_ohada_chart,
)



def referenced_account_ids(db, org_id: int) -> set[int]:
    """Account ids in `org` that appear in ANY transaction line (protected).

    Protecting both posted and draft references means re-running this script can
    never orphan a draft in progress or break a posted entry's account link.
    """
    return {
        aid
        for (aid,) in (
            db.query(TransactionLine.account_id)
            .join(
                Transaction,
                Transaction.id == TransactionLine.transaction_id,
            )
            .filter(
                Transaction.organization_id == org_id,
            )
            .distinct()
        )
    }


def reseed_ohada(db, org: Organization, dry: bool) -> dict:
    """Restore the real SYSCOHADA chart (replace stale illustrative accounts)."""
    protected = referenced_account_ids(db, org.id)
    existing = (
        db.query(Account)
        .filter(
            Account.organization_id == org.id,
            Account.framework == FrameworkCode.OHADA,
        )
        .all()
    )
    canonical_codes = {e["code"] for e in OHADA_CHART}
    stale = [
        a for a in existing
        if a.id not in protected
        and a.is_system_default
        and a.code not in canonical_codes
    ]
    kept = [a for a in existing if a.id in protected or not a.is_system_default]
    for a in stale:
        if not dry:
            db.delete(a)
    created = seed_ohada_chart(db, org, FrameworkCode.OHADA) if not dry else []
    if not dry:
        db.commit()
    final = (
        db.query(Account)
        .filter(
            Account.organization_id == org.id,
            Account.framework == FrameworkCode.OHADA,
        )
        .count()
        if not dry
        else len(existing) - len(stale) + len(created)
    )
    return {
        "framework": "OHADA",
        "existing": len(existing),
        "stale_removed": len(stale),
        "protected_kept": len(kept),
        "template_total": len(OHADA_CHART),
        "newly_seeded": len(created),
        "final_count": final,
    }


def reseed_ifrs(db, org: Organization, dry: bool) -> dict:
    """Restore Part-B compliance + the IAS-1 template (IFRS never has codes)."""
    protected = referenced_account_ids(db, org.id)
    existing = (
        db.query(Account)
        .filter(
            Account.organization_id == org.id,
            Account.framework == FrameworkCode.IFRS,
        )
        .all()
    )
    canonical_names = {e["name_en"] for e in IFRS_TEMPLATE}
    partb_corrected = 0
    removed = 0
    protected_kept = 0
    for a in existing:
        # Part B: ALL IFRS accounts must have code=NULL (IFRS has no mandated chart).
        if a.code is not None:
            partb_corrected += 1
            if not dry:
                a.code = None
        if a.id in protected:
            protected_kept += 1
        elif a.is_system_default and a.name_en not in canonical_names:
            removed += 1
            if not dry:
                db.delete(a)
        # user-created custom IFRS accounts (is_system_default=False) and any
        # system-default account already matching the template are kept as-is.

    if not dry:
        db.flush()
    created = seed_ifrs_template(db, org, FrameworkCode.IFRS) if not dry else []
    if not dry:
        db.commit()
    final = (
        db.query(Account)
        .filter(
            Account.organization_id == org.id,
            Account.framework == FrameworkCode.IFRS,
        )
        .count()
        if not dry
        else len(existing) - removed + len(created)
    )
    return {
        "framework": "IFRS",
        "existing": len(existing),
        "stale_removed": removed,
        "protected_kept": protected_kept,
        "partb_corrected": partb_corrected,
        "template_total": len(IFRS_TEMPLATE),
        "newly_seeded": len(created),
        "final_count": final,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--org", type=int, default=None, help="Organization id")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview only; write nothing"
    )
    parser.add_argument(
        "--demo-only",
        action="store_true",
        help="Only process orgs flagged is_demo (default processes ALL orgs: every "
        "workspace should have its framework's chart).",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        all_orgs = db.query(Organization).order_by(Organization.id).all()
        if args.demo_only:
            orgs = [o for o in all_orgs if o.is_demo]
        else:
            orgs = all_orgs
        if args.org is not None:
            orgs = [o for o in orgs if o.id == args.org]
        if not orgs:
            print("No matching organizations found.")
            return

        print(
            f"{'[DRY RUN] ' if args.dry_run else ''}Reseeding {len(orgs)} org(s):"
        )
        for org in orgs:
            before = db.query(Account).filter(
                Account.organization_id == org.id
            ).count()
            protected = referenced_account_ids(db, org.id)
            print(
                f"\n- org {org.id} {org.name!r} fw={org.framework.value} "
                f"is_demo={org.is_demo} accts_before={before} "
                f"protected_txn_accounts={len(protected)}"
            )
            if org.framework == FrameworkCode.IFRS:
                res = reseed_ifrs(db, org, args.dry_run)
            else:
                res = reseed_ohada(db, org, args.dry_run)
            print("  " + " | ".join(f"{k}={v}" for k, v in res.items()))

        if not args.dry_run:
            bad = (
                db.query(Account)
                .filter(
                    Account.framework == FrameworkCode.IFRS,
                    Account.code.isnot(None),
                )
                .count()
            )
            print(f"\nIFRS accounts with a non-null code (Part B violation): {bad}")
            for o in orgs:
                n = db.query(Account).filter(
                    Account.organization_id == o.id
                ).count()
                print(f"  org {o.id}: {n} account(s) after reseed")
    finally:
        db.close()

    if args.dry_run:
        print("\n[DRY RUN] No changes written.")


if __name__ == "__main__":
    main()

