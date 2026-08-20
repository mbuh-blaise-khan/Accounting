"""Seed the chart of accounts for an organization (per its framework).

OHADA workspaces get a REPRESENTATIVE subset of the real official SYSCOHADA
structure (2017 révisé) sourced from docs/ohada-ifrs-source-reference.md.
IFRS workspaces get an editable IAS-1-aligned starting template (IFRS has no
mandated chart of accounts). The OHADA seed is representative — not the full
~900-line official list. Deeper accounting conventions/measurement rules are
out of scope for this seed (structure + numbering only).

Usage (from the backend/ directory with the venv activated):

    python -m scripts.seed_coa <organization_id> [--framework OHADA|IFRS]

The framework defaults to the organization's own framework. Idempotent — safe
to run repeatedly (existing accounts are left untouched).
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
from app.models.enums import FrameworkCode  # noqa: E402
from app.models.organization import Organization  # noqa: E402
from app.services.account_service import seed_chart_for_organization  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("organization_id", type=int, help="Organization to seed")
    parser.add_argument(
        "--framework",
        type=str,
        choices=[fw.value for fw in FrameworkCode],
        default=None,
        help="Framework label for the seeded rows (defaults to the org's own)",
    )
    args = parser.parse_args()

    fw = FrameworkCode(args.framework) if args.framework else None
    db = SessionLocal()
    try:
        created = seed_chart_for_organization(
            db, organization_id=args.organization_id, framework=fw
        )
        # Resolve the framework actually used (defaults to the org's own).
        org = db.get(Organization, args.organization_id)
        framework_used = fw.value if fw else org.framework.value
    finally:
        db.close()

    definitions = len(OHADA_CHART) if framework_used != "IFRS" else len(IFRS_TEMPLATE)
    if framework_used != "IFRS":
        print(
            "Real official SYSCOHADA (2017 révisé) data — representative subset, not "
            "the full ~900-line list. Not for compliance use without review."
        )
    else:
        print(
            "IFRS editable starting template (IAS 1.54-aligned) — IFRS has no "
            "mandated chart of accounts, so no account codes are stored (Part B)."
        )
    print(
        f"Chart of accounts seed OK: {len(created)} new row(s) "
        f"(chart has {definitions} definitions total)."
    )


if __name__ == "__main__":
    main()
