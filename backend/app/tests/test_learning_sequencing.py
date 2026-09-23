"""Lesson sequencing + review-completion hotfix.

Focused learning-flow / review-queue regression net for the report that a
wrongly answered lesson question could reappear immediately as a "new" numbered
question, and that the review queue could leave the learner on a stale card:
- lesson questions render in the FIXED server order with no repeats;
- missed questions retry later through the review queue (never inside the
  numbered lesson sequence);
- the review queue visibly ends at zero due items;
- the expanded Lesson 1 is fully completable — all without weakening the
  certificate rule (every lesson: status == "completed" AND best_score == 100).

Covers the hotfix acceptance list: stable unique order; wrong answers do not
duplicate the numbered sequence; review cards are created/scheduled; flow
moves to the next distinct question; Lesson 1 reaches final position and the
normal complete state; correct review answers leave zero due items;
future-scheduled cards stay out of due-only results; wrong/guessed review
answers follow the C2 ladder/reset; certificate eligibility unchanged; C1
remediation still targets this lesson's own sections.
"""
from datetime import datetime, timedelta, timezone

from app.models.learning import Lesson
from app.tests.test_learning import (
    EXPECTED_SLUGS,
    _answer_keys,
    _attempt,
    _lesson_by_slug,
    _register,
)
from app.tests.test_learning_reviews import _answer_review, _parse_utc, _summary

SLUG = "what-is-accounting"

_TOLERANCE = timedelta(seconds=10)


def _questions(detail):
    return detail["questions"]


# --- 1) Stable, unique lesson order -----------------------------------------
def test_lesson1_question_order_is_stable_and_unique(client, test_db_session):
    """The detail payload is the fixed order: ids and positions each unique."""
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    ids = [q["id"] for q in _questions(detail)]
    positions = [q["position"] for q in _questions(detail)]
    assert len(ids) == len(set(ids)) > 0
    assert positions == sorted(positions)
    assert len(positions) == len(set(positions))
    rows = test_db_session.query(Lesson).filter(Lesson.slug == SLUG).all()
    assert len(rows) == 1  # no duplicate lesson
    assert rows[0].position == 1
    assert [l for l in client.get("/learning/lessons").json()] != []


# --- 2/4) Wrong answers never repeat inside the numbered lesson flow --------
def test_wrong_answer_does_not_repeat_the_lesson_question(client, test_db_session):
    """A wrong lesson answer returns feedback but the SAME question is never
    a second numbered question: ids stay unique per attempt target."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = _questions(detail)
    assert len(qs) >= 3
    q = qs[2]
    _correct, wrong = _answer_keys(test_db_session, q["id"])

    res = _attempt(client, lesson["id"], q["id"], option_key=wrong)
    assert res["is_correct"] is False
    assert res["question_id"] == q["id"]
    assert res["feedback"]["remediation"] is not None  # C1 still offered

    # The normal sequence, served again, is the SAME fixed list — no question
    # was re-inserted, duplicated, or reordered by the wrong answer.
    _lesson2, detail2 = _lesson_by_slug(client, SLUG)
    assert [x["id"] for x in _questions(detail2)] == [x["id"] for x in qs]
    nxt = _questions(detail2)[3]
    assert nxt["id"] != q["id"]  # the next question is a DISTINCT question
    assert nxt["position"] == q["position"] + 1  # counter moves on exactly +1


# --- 3) Wrong answers schedule reviews --------------------------------------
def test_wrong_lesson_answer_schedules_a_review_card(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    q = _questions(detail)[4]
    _correct, wrong = _answer_keys(test_db_session, q["id"])

    _attempt(client, lesson["id"], q["id"], option_key=wrong)
    cards = client.get("/learning/reviews").json()
    assert len(cards) == 1
    assert cards[0]["question_id"] == q["id"]
    assert cards[0]["is_due"] is True


# --- 5) Lesson 1 reaches its final question and the normal complete state ---
def test_lesson1_reaches_final_question_and_completes(client, test_db_session):
    """Walk the whole fixed order (correct each time): final position served,
    then progress flips to completed with a perfect score."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = _questions(detail)

    for q in qs:
        if q["kind"] == "mcq":
            correct, _w = _answer_keys(test_db_session, q["id"])
            r = _attempt(client, lesson["id"], q["id"], option_key=correct)
        else:
            r = _attempt(client, lesson["id"], q["id"], text="liability")
        assert r["is_correct"] is True
    # The last payload in server order is the final question.
    assert qs[-1]["position"] == len(qs)

    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_total"] == len(qs)
    assert progress["questions_answered"] == len(qs)
    assert progress["questions_correct"] == len(qs)
    assert progress["status"] == "completed"
    assert progress["best_score"] == 100
    # The "complete" banner inputs exist exactly as LessonDetailPage consumes.
    for key in ("status", "best_score", "questions_total",
                "questions_answered", "questions_correct", "practice_posted"):
        assert key in progress


# --- 6/7) Due queue empties visibly after the final due review ----------------
def test_final_correct_due_review_leaves_zero_due_items(client, test_db_session):
    """Two due cards, both answered correctly: due list AND summary agree on
    zero remaining — the caught-up state has something real to read."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    for q in (_questions(detail)[0], _questions(detail)[1]):
        _correct, wrong = _answer_keys(test_db_session, q["id"])
        _attempt(client, lesson["id"], q["id"], option_key=wrong)
    cards = client.get("/learning/reviews").json()
    assert len(cards) == 2

    for card in cards:
        q = next(x for x in _questions(detail) if x["id"] == card["question_id"])
        correct, _w = _answer_keys(test_db_session, q["id"])
        res = _answer_review(client, card["id"], option_key=correct)
        assert res["correct"] is True

    assert client.get("/learning/reviews", params={"due_only": "true"}).json() == []
    summary = _summary(client)
    assert summary["due_now"] == 0
    assert summary["total_active"] == 2  # cards still exist — just not due


# --- 8) Future-scheduled cards never appear as due ---------------------------
def test_future_scheduled_cards_stay_out_of_due_only(client, test_db_session):
    """A correctly answered review (due +1 day) is scheduled, shown in the
    summary, but absent from every due-only read."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    q = _questions(detail)[0]
    correct, wrong = _answer_keys(test_db_session, q["id"])
    _attempt(client, lesson["id"], q["id"], option_key=wrong)

    card = client.get("/learning/reviews").json()[0]
    res = _answer_review(client, card["id"], option_key=correct)
    assert res["correct"] is True
    due = _parse_utc(res["due_at"])
    assert due - datetime.now(timezone.utc) > timedelta(hours=12)  # ~1 day ahead

    assert client.get("/learning/reviews", params={"due_only": "true"}).json() == []
    summary = _summary(client)
    assert summary["due_now"] == 0
    assert summary["scheduled"] == 1
    assert summary["next_due_at"] is not None
    # Full list (no filter) still shows it — it is hidden from DUE view only.
    assert len(client.get("/learning/reviews").json()) == 1


# --- 9) C2 reset rules survive the hotfix ------------------------------------
def test_wrong_review_answer_stays_due_and_resets_stage(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    q = _questions(detail)[2]
    correct, wrong = _answer_keys(test_db_session, q["id"])
    _attempt(client, lesson["id"], q["id"], option_key=wrong)
    card = client.get("/learning/reviews").json()[0]

    before = datetime.now(timezone.utc)
    res = _answer_review(client, card["id"], option_key=wrong)
    assert res["correct"] is False
    assert res["stage"] == 0
    assert res["interval_days"] is None
    due = _parse_utc(res["due_at"])
    assert due >= before and abs(due - before) < _TOLERANCE

    due_only = client.get("/learning/reviews", params={"due_only": "true"}).json()
    assert len(due_only) == 1 and due_only[0]["is_due"] is True


# --- 10) Certificate rule unchanged ------------------------------------------
def test_certificate_eligibility_rule_unchanged(client, test_db_session):
    """Course completion still requires all 7 lessons completed at
    best_score 100 — Lesson 1 completed alone never unlocks the certificate."""
    from app.services import certificate_service
    from app.models.user import User

    _register(client)
    user = test_db_session.query(User).filter(
        User.email == "learner@example.com"
    ).first()
    lesson, detail = _lesson_by_slug(client, SLUG)
    for q in _questions(detail):
        if q["kind"] == "mcq":
            correct, _w = _answer_keys(test_db_session, q["id"])
            _attempt(client, lesson["id"], q["id"], option_key=correct)
        else:
            _attempt(client, lesson["id"], q["id"], text="liability")

    total, completed = certificate_service.course_completion_metrics(
        test_db_session, user
    )
    assert total == 7 and completed == 1
    assert client.post("/learning/certificate").status_code == 403


# --- 11) C1 remediation pin (this lesson's own sections only) ------------------
def test_wrong_lesson_answer_still_offers_own_lesson_remediation(
    client, test_db_session
):
    """Part C1 invariant re-pinned on the expanded Lesson 1: remediation
    targets a section of THIS lesson only."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    section_ids = {s["id"] for s in detail["sections"]}
    q = _questions(detail)[3]
    _correct, wrong = _answer_keys(test_db_session, q["id"])
    res = _attempt(client, lesson["id"], q["id"], option_key=wrong)
    rem = res["feedback"]["remediation"]
    assert rem is not None
    assert rem["lesson_id"] == lesson["id"]
    assert rem["section_id"] in section_ids
