"""Spaced-review + confidence tests (Session 11 Part C2).

Covers the Part C2 acceptance points:
1. A wrong lesson answer creates a review card due immediately.
2. A correct answer marked 'guessed' ("I got it, but I guessed") does the same.
3. A correct answer marked 'understood' ("I understand this") never creates one.
4. Duplicates are impossible: one card per (user, question), ever.
5. Review data is strictly user-scoped (list + answer + 404 for others).
6. Correct review answers advance the deterministic ladder 1/3/7/14 days;
   incorrect ones reset to stage 0, due immediately. All UTC-aware.
7. Review endpoints never expose the answer key.
8. Review answers create no `attempts` rows and never move lesson progress or
   certificate status.
9. Existing lesson behavior (scoring, practice connector) is unchanged —
   covered by test_learning.py, re-run with the full suite.
"""
from datetime import datetime, timedelta, timezone

from app.models.learning import Attempt, ReviewItem

from app.tests.test_learning import (
    _answer_keys,
    _attempt,
    _lesson_by_slug,
    _register,
)

_TOLERANCE = timedelta(seconds=10)


def _reviews(client):
    r = client.get("/learning/reviews")
    assert r.status_code == 200, r.text
    return r.json()


def _summary(client):
    r = client.get("/learning/reviews/summary")
    assert r.status_code == 200, r.text
    return r.json()


def _answer_review(client, review_id, lang=None, **extra):
    url = f"/learning/reviews/{review_id}/answer" + (f"?lang={lang}" if lang else "")
    r = client.post(url, json=extra)
    assert r.status_code == 200, r.text
    return r.json()


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    assert parsed.tzinfo is not None  # UTC-consistent, offset-carrying
    return parsed.astimezone(timezone.utc)


def _make_review(client, test_db_session, slug="what-is-accounting", q_index=0):
    """(lesson, question, review_id) — one wrong lesson answer creates the card."""
    lesson, detail = _lesson_by_slug(client, slug)
    q = detail["questions"][q_index]
    correct_key, wrong_key = _answer_keys(test_db_session, q["id"])
    _attempt(client, lesson["id"], q["id"], option_key=wrong_key)
    card = _reviews(client)[0]
    return lesson, q, correct_key, wrong_key, card["id"]


# --- 1) Creation rules ---------------------------------------------------------
def test_wrong_answer_creates_a_due_review_card(client, test_db_session):
    _register(client)
    lesson, q, _correct, wrong, review_id = _make_review(client, test_db_session)

    cards = _reviews(client)
    assert len(cards) == 1
    card = cards[0]
    assert card["id"] == review_id
    assert card["question_id"] == q["id"]
    assert card["lesson_id"] == lesson["id"]
    assert card["stage"] == 0
    assert card["last_outcome"] == "wrong"
    assert card["is_due"] is True
    due = _parse_utc(card["due_at"])
    assert abs(due - datetime.now(timezone.utc)) < _TOLERANCE

    summary = _summary(client)
    assert summary["total_active"] == 1
    assert summary["due_now"] == 1
    assert summary["scheduled"] == 0


def test_guessed_correct_answer_creates_a_review_card(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]
    correct_key, _wrong = _answer_keys(test_db_session, q["id"])

    res = _attempt(
        client, lesson["id"], q["id"], option_key=correct_key, confidence="guessed"
    )
    assert res["is_correct"] is True  # confidence never changes the score

    cards = _reviews(client)
    assert len(cards) == 1
    assert cards[0]["question_id"] == q["id"]
    assert cards[0]["stage"] == 0
    assert cards[0]["last_outcome"] == "guessed"
    assert cards[0]["is_due"] is True


def test_confident_correct_answer_creates_no_review(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]
    correct_key, _wrong = _answer_keys(test_db_session, q["id"])

    res = _attempt(
        client, lesson["id"], q["id"], option_key=correct_key, confidence="understood"
    )
    assert res["is_correct"] is True

    assert _reviews(client) == []
    summary = _summary(client)
    assert summary["total_active"] == 0
    assert summary["due_now"] == 0


def test_correct_answer_without_confidence_creates_no_review(client, test_db_session):
    """Older clients that send no confidence field keep the old behaviour."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]
    correct_key, _wrong = _answer_keys(test_db_session, q["id"])

    _attempt(client, lesson["id"], q["id"], option_key=correct_key)
    assert _reviews(client) == []


def test_wrong_answer_with_understood_confidence_still_creates_review(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]
    _correct, wrong_key = _answer_keys(test_db_session, q["id"])

    _attempt(
        client, lesson["id"], q["id"], option_key=wrong_key, confidence="understood"
    )
    cards = _reviews(client)
    assert len(cards) == 1
    assert cards[0]["last_outcome"] == "wrong"


def test_invalid_confidence_value_is_rejected(client):
    _register(client)
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]
    r = client.post(
        "/learning/attempts",
        json={
            "lesson_id": lesson["id"],
            "question_id": q["id"],
            "option_key": "A",
            "confidence": "maybe",
        },
    )
    assert r.status_code == 422


# --- 2) Duplicate prevention ---------------------------------------------------
def test_no_duplicate_active_reviews_for_same_user_question(client, test_db_session):
    _register(client)
    lesson, q, _correct, wrong_key, _rid = _make_review(client, test_db_session)

    # Two more wrong answers on the SAME question must reuse the same card.
    _attempt(client, lesson["id"], q["id"], option_key=wrong_key)
    _attempt(client, lesson["id"], q["id"], option_key=wrong_key)

    rows = test_db_session.query(ReviewItem).all()
    assert len(rows) == 1  # unique (user_id, question_id) — no duplicates, ever
    assert len(_reviews(client)) == 1


# --- 3) User scoping -----------------------------------------------------------
def test_reviews_are_strictly_user_scoped(client, test_db_session):
    _register(client, email="alice@example.com", name="Alice")
    _lesson, _q, _c, _w, alice_review_id = _make_review(client, test_db_session)

    # Bob takes over the session cookie: Alice's card is invisible to him.
    _register(client, email="bob@example.com", name="Bob")
    assert _reviews(client) == []
    bob_summary = _summary(client)
    assert bob_summary["total_active"] == 0

    r = client.post(
        f"/learning/reviews/{alice_review_id}/answer", json={"option_key": "A"}
    )
    assert r.status_code == 404  # not found — never leaks another user's card

    # And Bob's own wrong answer creates HIS card, separate from Alice's.
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]
    _correct, wrong_key = _answer_keys(test_db_session, q["id"])
    _attempt(client, lesson["id"], q["id"], option_key=wrong_key)
    bob_cards = _reviews(client)
    assert len(bob_cards) == 1 and bob_cards[0]["id"] != alice_review_id


def test_review_endpoints_require_authentication(client):
    for path in ("/learning/reviews", "/learning/reviews/summary"):
        r = client.get(path)
        assert r.status_code in (401, 403), (path, r.status_code)
    r = client.post("/learning/reviews/1/answer", json={"option_key": "A"})
    assert r.status_code in (401, 403)


# --- 4) Deterministic scheduling ladder ----------------------------------------
def test_correct_review_answers_advance_the_ladder(client, test_db_session):
    _register(client)
    _lesson, q, correct_key, _wrong, review_id = _make_review(client, test_db_session)

    # stage 0 -> 1 day (new stage 1)
    res = _answer_review(client, review_id, option_key=correct_key)
    assert res["correct"] is True and res["stage"] == 1
    assert res["interval_days"] == 1
    due = _parse_utc(res["due_at"])
    assert abs(due - (datetime.now(timezone.utc) + timedelta(days=1))) < _TOLERANCE

    # stage 1 -> 3 days (new stage 2)
    res = _answer_review(client, review_id, option_key=correct_key)
    assert res["stage"] == 2 and res["interval_days"] == 3
    due = _parse_utc(res["due_at"])
    assert abs(due - (datetime.now(timezone.utc) + timedelta(days=3))) < _TOLERANCE

    # stage 2 -> 7 days (new stage 3)
    res = _answer_review(client, review_id, option_key=correct_key)
    assert res["stage"] == 3 and res["interval_days"] == 7
    due = _parse_utc(res["due_at"])
    assert abs(due - (datetime.now(timezone.utc) + timedelta(days=7))) < _TOLERANCE

    # stage 3+ -> 14 days (interval caps, stage keeps counting)
    res = _answer_review(client, review_id, option_key=correct_key)
    assert res["stage"] == 4 and res["interval_days"] == 14
    due = _parse_utc(res["due_at"])
    assert abs(due - (datetime.now(timezone.utc) + timedelta(days=14))) < _TOLERANCE

    summary = _summary(client)
    assert summary["total_active"] == 1
    assert summary["due_now"] == 0
    assert summary["scheduled"] == 1
    assert summary["next_due_at"] is not None


def test_incorrect_review_answer_resets_to_stage_zero(client, test_db_session):
    _register(client)
    _lesson, q, correct_key, wrong_key, review_id = _make_review(
        client, test_db_session
    )

    # Climb to stage 2 first.
    _answer_review(client, review_id, option_key=correct_key)
    _answer_review(client, review_id, option_key=correct_key)
    assert _reviews(client)[0]["stage"] == 2

    before = datetime.now(timezone.utc)
    res = _answer_review(client, review_id, option_key=wrong_key)
    assert res["correct"] is False
    assert res["stage"] == 0
    assert res["interval_days"] is None  # reset — no interval was scheduled
    due = _parse_utc(res["due_at"])
    assert due >= before and abs(due - before) < _TOLERANCE  # due immediately

    card = _reviews(client)[0]
    assert card["stage"] == 0 and card["is_due"] is True
    assert card["last_outcome"] == "review_wrong"


def test_due_only_filter_matches_the_summary(client, test_db_session):
    """A card created now (due immediately) is due until answered — the
    due_only list and the summary agree with each other."""
    _register(client)
    _lesson, _q, _c, _w, _rid = _make_review(client, test_db_session)
    due_only = client.get("/learning/reviews", params={"due_only": "true"}).json()
    assert len(due_only) == 1
    assert _summary(client)["due_now"] == 1


# --- 5) Answer-key protection ---------------------------------------------------
def test_review_endpoints_never_expose_the_answer_key(client, test_db_session):
    _register(client)
    # Use the short-answer question too: accepted texts must never appear.
    lesson2, detail2 = _lesson_by_slug(client, "the-accounting-equation")
    sa = next(q for q in detail2["questions"] if q["kind"] == "short_answer")
    _attempt(client, lesson2["id"], sa["id"], text="liabilities")

    raw_list = client.get("/learning/reviews").text
    for forbidden in (
        "correct_option_key",
        "correct_text",
        "is_correct",
        "short_answer_en",
        "short_answer_fr",
    ):
        assert forbidden not in raw_list, forbidden

    card = _reviews(client)[0]
    for option in card["answers"]:
        assert set(option.keys()) == {"option_key", "text_en", "text_fr"}

    res = _answer_review(client, card["id"], text="equity")
    assert res["correct"] is True  # accepted EN text still scores (as in lessons)
    raw_answer = str(res)
    for forbidden in ("correct_option_key", "correct_text", "is_correct"):
        assert forbidden not in raw_answer, forbidden
    assert set(res.keys()) == {
        "review_id",
        "question_id",
        "correct",
        "stage",
        "due_at",
        "interval_days",
        "feedback",
    }


# --- 6) Review data never moves lesson progress or certificates -----------------
def test_review_answers_do_not_change_progress_or_completion(
    client, test_db_session
):
    _register(client)
    # Baseline lesson progress: one correct lesson attempt.
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]
    correct_key, _wrong_key = _answer_keys(test_db_session, q["id"])
    _attempt(client, lesson["id"], q["id"], option_key=correct_key)
    base_progress = _lesson_by_slug(client, "what-is-accounting")[1]["progress"]
    base_completion = client.get("/learning/completion").json()

    # A review card for a DIFFERENT lesson's question (wrong lesson answer).
    rid_lesson, rid_q, rid_correct, _rid_wrong, _rid = _make_review(
        client, test_db_session, slug="the-accounting-equation"
    )

    # Several review interactions…
    _answer_review(client, _rid, option_key=rid_correct)
    _answer_review(client, _rid, option_key=rid_correct)

    # …change NO lesson progress and NO completion/certificate status.
    after_progress = _lesson_by_slug(client, "what-is-accounting")[1]["progress"]
    assert after_progress == base_progress
    after_completion = client.get("/learning/completion").json()
    assert after_completion == base_completion

    attempts = test_db_session.query(Attempt).count()
    assert attempts == 2  # review answers create no `attempts` rows