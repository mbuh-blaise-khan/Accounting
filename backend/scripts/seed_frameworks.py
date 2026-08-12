"""Seed the default framework registry (OHADA + IFRS with a current version each).

Idempotent — safe to run repeatedly. Run from the backend/ directory with the
venv activated:

    python -m scripts.seed_frameworks
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal  # noqa: E402
from app.services.framework_service import ensure_default_frameworks  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        created = ensure_default_frameworks(db)
        print(f"Framework seed OK. Created {len(created)} new framework row(s); "
              "existing ones were kept up to date.")
    finally:
        db.close()


if __name__ == "__main__":
    main()