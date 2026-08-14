"""Seed the ILLUSTRATIVE (demo) chart of accounts for an organization.

IMPORTANT: this seeds DEMO data only — a small, plain-language chart meant to
prove the accounting engine works end-to-end. It is NOT an official OHADA or
IFRS chart. Replace with a reviewed / licensed official chart before any real
production or compliance use.

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

from app.core.database import SessionLocal  # noqa: E402
from app.models.enums import FrameworkCode  # noqa: E402
from app.services.account_service import (  # noqa: E402
    ILLUSTRATIVE_CHART,
    seed_illustrative_chart,
)


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
        created = seed_illustrative_chart(
            db, organization_id=args.organization_id, framework=fw
        )
    finally:
        db.close()

    print(
        "ILLUSTRATIVE DEMO DATA — replace with a reviewed/licensed official "
        "chart before any real production or compliance use."
    )
    print(
        f"Chart of accounts seed OK: {len(created)} new row(s) "
        f"(chart has {len(ILLUSTRATIVE_CHART)} definitions total)."
    )


if __name__ == "__main__":
    main()
