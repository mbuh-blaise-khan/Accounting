"""Backfill-script tests (Session 17).

`scripts.recompute_progress` must heal legacy `progress` rows inflated by the
old raw-row rollup using the SAME deterministic rule the API uses
(`_refresh_progress`: distinct questions, latest attempt per question), preview
without writing, be idempotent, rebuild rows missing entirely, and never
rewrite the `completed_at` of a legitimately-completed lesson.

Canonical run (from backend/):
    python -m pytest app/tests/test_progress_backfill.py -q
"""
from datetime import datetime

from app.models.learning import LessonProgress
from app.tests.test_learning import (
    _answer_keys,
    _attempt,
    _correct_answer_payload,
    _lesson_by_slug,
    _register,
)
from scripts.recompute_progress import recompute_progress

_SLUG = "what-is-accounting"


def _row(db, lesson_id):
    return (
        db.query(LessonProgress)
        .filter(LessonProgress.lesson_id == lesson_id)
        .one()
    )


def _answer_all_correct(client, db, lesson, detail):
    """Grade every question correctly (stored MCQ key or the stored accepted
    short-answer text, read straight from the DB — same pattern as
    test_lesson1_expansion)."""
    for q in detail["questions"]:
        r = _attempt(client, lesson["id"], q["id"],
                     **_correct_answer_payload(db, q))
        assert r["is_correct"] is True, q["position"]


def test_recompute_heals_inflated_row_previews_and_is_idempotent(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, _SLUG)
    q = detail["questions"][0]
    correct, wrong = _answer_keys(test_db_session, q["id"])

    # Ten raw attempt rows on ONE question (4 wrong, then 6 correct). The OLD
    # raw-row rollup would have stored exactly: 10 answered / 6 correct / 60%
    # / falsely "completed" (raw rows >= total), though only 1 question was
    # ever visited.
    for key in (wrong, wrong, wrong, wrong, correct, correct, correct,
                correct, correct, correct):
        _attempt(client, lesson["id"], q["id"], option_key=key)

    row = _row(test_db_session, lesson["id"])
    row.status = "completed"
    row.best_score = 60
    row.questions_answered = 10
    row.questions_correct = 6
    row.completed_at = datetime(2026, 2, 1, 12, 0)  # legacy completion stamp
    test_db_session.commit()

    # 1) Dry-run reports the heal but writes NOTHING.
    stats = recompute_progress(test_db_session, dry=True)
    assert stats["changed"] == 1 and stats["created"] == 0
    test_db_session.expire_all()
    row = _row(test_db_session, lesson["id"])
    assert row.questions_answered == 10 and row.status == "completed"

    # 2) Real run applies distinct/latest: 10 raw rows -> 1 question visited.
    stats = recompute_progress(test_db_session, dry=False)
    assert stats["changed"] == 1
    test_db_session.expire_all()
    row = _row(test_db_session, lesson["id"])
    assert row.questions_answered == 1
    assert row.questions_correct == 1  # the LATEST attempt is correct
    assert row.best_score == 100
    assert row.status == "in_progress"  # 1 of 18 visited — false completion gone
    assert row.completed_at is None

    # 3) Idempotent: an immediate second run changes nothing.
    stats = recompute_progress(test_db_session, dry=False)
    assert stats["changed"] == 0


def test_recompute_recreates_missing_progress_row_from_attempts(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, _SLUG)
    q = detail["questions"][0]
    correct, wrong = _answer_keys(test_db_session, q["id"])
    _attempt(client, lesson["id"], q["id"], option_key=wrong)
    _attempt(client, lesson["id"], q["id"], option_key=correct)

    # The stored row vanished but attempts remain -> the pair must be rebuilt
    # from the attempts side of the union.
    test_db_session.delete(_row(test_db_session, lesson["id"]))
    test_db_session.commit()

    stats = recompute_progress(test_db_session, dry=False)
    assert stats["changed"] == 1 and stats["created"] == 1
    test_db_session.expire_all()
    row = _row(test_db_session, lesson["id"])
    assert row.questions_answered == 1 and row.questions_correct == 1
    assert row.best_score == 100 and row.status == "in_progress"


def test_recompute_preserves_completed_at_on_legitimate_completion(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, _SLUG)
    _answer_all_correct(client, test_db_session, lesson, detail)

    fixed = datetime(2026, 2, 1, 12, 0)
    row = _row(test_db_session, lesson["id"])
    assert row.status == "completed" and row.best_score == 100
    row.completed_at = fixed
    test_db_session.commit()

    # A legitimately-completed lesson recomputes to IDENTICAL values — the
    # refresh must not rewrite its completion timestamp (changed == 0 proves
    # the preserved completed_at matched the stored one exactly).
    stats = recompute_progress(test_db_session, dry=False)
    assert stats["changed"] == 0 and stats["created"] == 0
    test_db_session.expire_all()
    row = _row(test_db_session, lesson["id"])
    assert row.completed_at == fixed
    assert row.status == "completed" and row.best_score == 100
    assert row.questions_answered == 18 and row.questions_correct == 18
