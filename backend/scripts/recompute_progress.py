"""Recompute stored lesson-progress rows with the Session 17 roll-up rule.

WHY THIS EXISTS
---------------
Before Session 17, `_refresh_progress` counted RAW attempt rows, so `progress`
rows written by older builds can hold inflated values (the reported
"55 answered / 18 total"), falsely-`completed` statuses and unreachable
`best_score == 100`. Rows now self-heal whenever the learner submits another
attempt in that lesson, but a lesson the learner never re-enters keeps its
stale row forever. This script recomputes EVERY stored row — plus any
(user, lesson) pair that has attempts but no row — by calling the exact
`_refresh_progress` the API uses, so the rule can never diverge.

Semantics re-applied (deterministic, no AI): each question counts once, judged
by its LATEST attempt; completion requires every question visited at least once.

Guarantees:
- Idempotent: a second run reports 0 changed rows.
- `completed_at` is preserved when a row was already `completed` and stays
  `completed` — recomputing counts must never rewrite the completion
  timestamp of a legitimately-finished lesson.
- `--dry-run` previews the exact field-level diff and writes NOTHING (it
  rolls back the session at the end, so commit any setup state first).

Usage (from backend/ with the venv active):

    .venv/Scripts/python.exe -m scripts.recompute_progress              # fix all rows
    .venv/Scripts/python.exe -m scripts.recompute_progress --dry-run    # preview only
"""
import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal  # noqa: E402
from app.learning.service import _refresh_progress  # noqa: E402
from app.models.learning import Attempt, Lesson, LessonProgress  # noqa: E402
from app.models.user import User  # noqa: E402

# The fields a recompute is allowed to change. `updated_at` is deliberately
# excluded (it bumps on any UPDATE and says nothing about correctness) and
# `id`/`user_id`/`lesson_id` are the pair identity itself.
_PROGRESS_FIELDS = (
    "status",
    "best_score",
    "questions_answered",
    "questions_correct",
    "practice_posted",
    "completed_at",
)


def _snapshot(row: LessonProgress | None) -> dict | None:
    """Plain-dict copy of the recompute-relevant fields (None if no row)."""
    if row is None:
        return None
    return {f: getattr(row, f) for f in _PROGRESS_FIELDS}


def progress_pairs(db) -> set[tuple[int, int]]:
    """Every (user_id, lesson_id) that has a stored row OR any attempt.

    The attempts side catches legacy pairs whose progress row is missing
    entirely; the rows side catches rows whose attempts were pruned.
    """
    pairs = {
        (uid, lid)
        for uid, lid in db.query(
            LessonProgress.user_id, LessonProgress.lesson_id
        ).all()
    }
    pairs.update(
        (uid, lid)
        for uid, lid in db.query(Attempt.user_id, Attempt.lesson_id).distinct().all()
    )
    return pairs


def recompute_progress(db, dry: bool = False) -> dict:
    """Re-derive every progress pair through `_refresh_progress`.

    Returns {"scanned", "changed", "created", "rows"} where `rows` holds a
    per-field before/after diff for each changed pair. With `dry=True` the
    recomputes are rolled back at the end — the session must not hold
    uncommitted work when calling this.
    """
    stats: dict = {"scanned": 0, "changed": 0, "created": 0, "rows": []}
    for user_id, lesson_id in sorted(progress_pairs(db)):
        if user_id is None or lesson_id is None:
            continue
        user = db.get(User, user_id)
        lesson = db.get(Lesson, lesson_id)
        if user is None or lesson is None:  # orphaned pair — nothing to recompute
            continue

        existing = (
            db.query(LessonProgress)
            .filter(
                LessonProgress.user_id == user_id,
                LessonProgress.lesson_id == lesson_id,
            )
            .first()
        )
        before = _snapshot(existing)
        was_completed_at = existing.completed_at if existing is not None else None

        row = _refresh_progress(db, user, lesson)

        # Preserve the completion timestamp across recomputes of rows that
        # were already completed and remain completed (see module docstring).
        if before is not None and before["status"] == "completed":
            if row.status == "completed":
                row.completed_at = was_completed_at

        after = _snapshot(row)
        stats["scanned"] += 1
        if before != after:
            stats["changed"] += 1
            if before is None:
                stats["created"] += 1
            stats["rows"].append(
                {
                    "user_id": user_id,
                    "lesson_id": lesson_id,
                    "before": before,
                    "after": after,
                }
            )
        if not dry:
            db.commit()

    if dry:
        db.rollback()  # undo every recompute — the preview writes nothing
    return stats


def _fmt_change(change: dict) -> str:
    head = f"user={change['user_id']} lesson={change['lesson_id']}"
    before = change["before"]
    if before is None:
        after = change["after"]
        return f"{head}: NEW row -> " + ", ".join(
            f"{f}={after[f]!r}" for f in _PROGRESS_FIELDS
        )
    diffs = [
        f"{f}: {before[f]!r} -> {change['after'][f]!r}"
        for f in _PROGRESS_FIELDS
        if before[f] != change["after"][f]
    ]
    return f"{head}: " + ", ".join(diffs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview every field-level change; write nothing",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        stats = recompute_progress(db, dry=args.dry_run)
        prefix = "[DRY RUN] " if args.dry_run else ""
        print(
            f"{prefix}Scanned {stats['scanned']} progress pair(s): "
            f"{stats['changed']} changed ({stats['created']} would be created)"
        )
        for change in stats["rows"]:
            print("  - " + _fmt_change(change))
    finally:
        db.close()

    if args.dry_run:
        print("\n[DRY RUN] No changes written.")


if __name__ == "__main__":
    main()

