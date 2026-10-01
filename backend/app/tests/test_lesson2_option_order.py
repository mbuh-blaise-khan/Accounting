"""Lesson 2 option-display-order tests (assessment-quality hotfix).

DEFECT: `Question.answers` is loaded `ORDER BY position` (seed order) and both
read paths serialized that list verbatim, so — because every Lesson 2
closed-ended question was authored with the correct answer first — the correct
answer was rendered in displayed position 1 for EVERY question. A learner could
score 100% by always picking the first option, with no accounting understood.

FIX (deterministic, display-only): the stored answer rows are never changed.
`_display_answers` returns a NEW, deterministically permuted list seeded from
the immutable `questions.id` and `answers.id`, used by BOTH `get_lesson` and
`_review_item_out`. Grading still resolves the submitted `option_key` to its
`Answer` row by id, so correctness, attempts, review items, progress, mastery,
remediation and the certificate rule are untouched.

These tests pin:
1. Every eligible closed-ended Lesson 2 question has valid, unique answer ids.
2. The correct answer is NOT always rendered in position 1.
3. Correct-answer positions are reasonably distributed across the available
   positions (exempting documented meaningful-order questions).
4. Correct-answer semantics and grading by answer id are unchanged.
5. The same question returns the same display order after repeat fetch,
   refresh/resume and review rendering, and in both EN and FR.
6. Attempts, review items, progress, mastery and certificate behavior stay
   compatible.
7. Lesson 1's answer ordering and integrity safeguards are unchanged.
"""
from collections import Counter

from app.learning.service import (
    _MEANINGFUL_OPTION_ORDER,
    _OPTION_ORDER_LESSON_SLUGS,
    _display_answers,
)
from app.models.learning import Answer, Attempt, Lesson, Question
from app.tests.test_learning import (
    _answer_keys,
    _attempt,
    _correct_answer_payload,
    _lesson_by_slug,
    _register,
)
from app.tests.test_learning_reviews import _answer_review, _reviews

SLUG = "the-accounting-equation"
L1_SLUG = "what-is-accounting"


def _displayed_keys(detail):
    """{question_id: [option_key, ...]} in the order the API served them."""
    return {
        q["id"]: [a["option_key"] for a in q["answers"]]
        for q in detail["questions"]
    }


def _stored_keys(session, question_id):
    """([stored option_keys in position order], correct option_key or None).

    A short-answer question has no answer rows at all, hence the None.
    """
    rows = (
        session.query(Answer)
        .filter(Answer.question_id == question_id)
        .order_by(Answer.position)
        .all()
    )
    correct = next((a.option_key for a in rows if a.is_correct), None)
    return [a.option_key for a in rows], correct
# --- 1) Valid, unique answer ids on every eligible question -------------------
def test_every_closed_ended_question_has_valid_unique_answers(
    client, test_db_session
):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    seen = []
    for q in detail["questions"]:
        if q["kind"] != "mcq":
            assert q["answers"] == []  # short answers expose no options
            continue
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == q["id"])
            .order_by(Answer.position)
            .all()
        )
        assert len(rows) >= 2
        assert len({a.id for a in rows}) == len(rows)       # unique ids
        assert [a.position for a in rows] == list(range(1, len(rows) + 1))
        assert len({a.option_key for a in rows}) == len(rows)
        assert all(a.text_en and a.text_fr for a in rows)
        assert sum(1 for a in rows if a.is_correct) == 1    # one correct answer
        assert len(q["answers"]) == len(rows)               # all options served
        assert {a["option_key"] for a in q["answers"]} == {a.option_key
                                                          for a in rows}
        seen.extend(a.id for a in rows)
    assert len(seen) == len(set(seen))


# --- 2/3) Correct answers are distributed, not always first --------------------
def test_correct_answer_is_not_always_in_display_position_one(
    client, test_db_session
):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    exempt = _MEANINGFUL_OPTION_ORDER.get(SLUG, frozenset())
    positions = []
    for q in detail["questions"]:
        if q["kind"] != "mcq" or q["position"] in exempt:
            continue  # documented meaningful-order questions keep seeded order
        _keys, correct = _stored_keys(test_db_session, q["id"])
        served = [a["option_key"] for a in q["answers"]]
        positions.append(served.index(correct) + 1)
    assert positions, "no eligible closed-ended questions found"
    # The defect itself: it must not be "always the first option".
    assert len(set(positions)) >= 2, (
        "correct answers still cluster in one displayed position: %s" % positions
    )
    # Reasonably distributed: with 3 options all three slots are used, and no
    # single slot takes an overwhelming majority.
    assert set(positions) == {1, 2, 3}
    top = Counter(positions).most_common(1)[0][1]
    assert top <= max(2, (len(positions) * 2) // 3)


# --- 4) Grading is by option key / answer id, not by display index ------------
def test_grading_uses_option_key_not_display_position(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    q = next(x for x in detail["questions"] if x["kind"] == "mcq")
    correct, wrong = _answer_keys(test_db_session, q["id"])
    # Whichever SLOT the correct option is displayed in, submitting its
    # option_key is correct and any other option_key is wrong — the displayed
    # index is irrelevant to grading.
    ok = _attempt(client, lesson["id"], q["id"], option_key=correct)
    assert ok["is_correct"] is True
    assert ok["correct_option_key"] == correct
    bad = _attempt(client, lesson["id"], q["id"], option_key=wrong)
    assert bad["is_correct"] is False
    # The meaning of each option is unchanged: the graded key still resolves to
    # the same stored text the learner was shown.
    stored = next(a for a in test_db_session.query(Answer)
                  .filter(Answer.question_id == q["id"])
                  .filter(Answer.option_key == correct).all())
    served = next(a for a in q["answers"] if a["option_key"] == correct)
    assert served["text_en"] == stored.text_en
    assert served["text_fr"] == stored.text_fr


def test_stored_answer_rows_are_never_reordered_or_rewritten(
    client, test_db_session
):
    """The display permutation is a COPY: storage keeps position/key/semantics."""
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    before = {}
    for q in detail["questions"]:
        keys, correct = _stored_keys(test_db_session, q["id"])
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == q["id"])
            .order_by(Answer.position)
            .all()
        )
        before[q["id"]] = (
            keys, correct, [(a.id, a.position, a.is_correct) for a in rows],
        )
    # Answer several closed-ended questions (wrong then right) to exercise the
    # grading, review and re-sync paths.
    lesson = next(l for l in client.get("/learning/lessons").json()
                  if l["slug"] == SLUG)
    closed = [q for q in detail["questions"] if q["kind"] == "mcq"][:6]
    assert len(closed) == 6
    for q in closed:
        correct, wrong = _answer_keys(test_db_session, q["id"])
        _attempt(client, lesson["id"], q["id"], option_key=wrong)
        _attempt(client, lesson["id"], q["id"], option_key=correct)
    test_db_session.expire_all()
    for q in detail["questions"]:
        keys, correct = _stored_keys(test_db_session, q["id"])
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == q["id"])
            .order_by(Answer.position)
            .all()
        )
        assert before[q["id"]] == (
            keys, correct, [(a.id, a.position, a.is_correct) for a in rows],
        ), "stored answer row changed for question %s" % q["id"]


# --- 5) Stable display order: repeat fetch / resume / review / EN-FR ----------
def test_display_order_is_stable_across_refetch_resume_and_review(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    baseline = _displayed_keys(detail)

    # Repeat fetch + refresh/resume (the page re-fetches on mount and on lang).
    for _ in range(4):
        again = _displayed_keys(_lesson_by_slug(client, SLUG)[1])
        assert again == baseline

    # A wrong answer (feedback + retry path) must not disturb the order either.
    q = next(x for x in detail["questions"] if x["kind"] == "mcq")
    _correct, wrong = _answer_keys(test_db_session, q["id"])
    _attempt(client, lesson["id"], q["id"], option_key=wrong)
    assert _displayed_keys(_lesson_by_slug(client, SLUG)[1]) == baseline

    # The REVIEW queue renders the SAME order for the SAME question.
    card = _reviews(client)[0]
    review_detail = next(
        x for x in _lesson_by_slug(client, SLUG)[1]["questions"]
        if x["id"] == card["question_id"]
    )
    card_keys = [a["option_key"] for a in card["answers"]]
    assert card_keys == baseline[card["question_id"]]
    assert card_keys == [a["option_key"] for a in review_detail["answers"]]
    # ...and stays the same when the card is re-fetched after being answered.
    _answer_review(client, card["id"], option_key=_correct)
    assert _displayed_keys(_lesson_by_slug(client, SLUG)[1]) == baseline
    assert _displayed_keys(_lesson_by_slug(client, SLUG)[1]) == baseline


def test_display_order_is_language_independent(client):
    """Same option order in EN and FR (only the texts differ)."""
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    keys = {q["id"]: [a["option_key"] for a in q["answers"]]
            for q in detail["questions"]}
    texts_fr = {q["id"]: [a["text_fr"] for a in q["answers"]]
                for q in detail["questions"]}
    _lesson2, detail_fr = _lesson_by_slug(client, SLUG)
    keys_fr = {q["id"]: [a["option_key"] for a in q["answers"]]
               for q in detail_fr["questions"]}
    texts_en = {q["id"]: [a["text_en"] for a in q["answers"]]
                for q in detail["questions"]}
    assert keys == keys_fr                 # identical option ORDER
    assert texts_en != texts_fr            # but genuinely localized text


def test_display_order_is_a_pure_function_of_immutable_ids(client,
                                                            test_db_session):
    """The helper itself is deterministic and never mutates storage."""
    _register(client)
    summary = next(l for l in client.get("/learning/lessons").json()
                   if l["slug"] == SLUG)
    row = test_db_session.get(Lesson, summary["id"])
    stored_positions = {q.id: q.position for q in row.questions}
    mcq = [q for q in row.questions if q.kind == "mcq"][:3]
    assert mcq
    for q in mcq:
        runs = [[a.id for a in _display_answers(q, SLUG)] for _ in range(5)]
        assert all(r == runs[0] for r in runs)
        # A permutation: every stored answer appears exactly once.
        assert sorted(runs[0]) == sorted(a.id for a in q.answers)
        # Storage untouched by the helper.
        assert [a.position for a in q.answers] == sorted(
            a.position for a in q.answers)
        assert stored_positions[q.id] == q.position  # question position stable


# --- 6) Attempts / review / progress / mastery / certificate still compatible --
def test_attempts_review_mastery_and_certificate_still_work(client,
                                                            test_db_session):
    """A wrong answer (now shown at a non-first position) still scores wrong,
    schedules a review, and a correct review answer still restores mastery."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    by_pos = {q["position"]: q for q in qs}
    q5 = by_pos[5]
    _c5, w5 = _answer_keys(test_db_session, q5["id"])

    wrong = _attempt(client, lesson["id"], q5["id"], option_key=w5)
    assert wrong["is_correct"] is False           # graded by option_key
    assert wrong["feedback"]["remediation"] is not None
    card = _reviews(client)[0]
    assert card["question_id"] == q5["id"]

    for q in qs:
        if q["position"] == 5:
            continue
        _attempt(client, lesson["id"], q["id"],
                 **_correct_answer_payload(test_db_session, q))
    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_answered"] == 18
    assert progress["questions_correct"] == 17
    assert progress["best_score"] == 94
    assert progress["status"] == "completed"

    res = _answer_review(client, card["id"], option_key=_c5)
    assert res["correct"] is True
    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_correct"] == 18
    assert progress["best_score"] == 100

    # Certificate rule unchanged: one lesson alone never unlocks it.
    completion = client.get("/learning/completion").json()
    assert completion["completed_lessons"] == 1
    assert completion["total_lessons"] == 7
    assert completion["certificate_status"] == "locked"
    assert client.post("/learning/certificate").status_code == 403


# --- 7) Lesson 1 (and every other lesson) is untouched -----------------------
def test_lesson1_and_other_lessons_keep_seed_answer_order(client,
                                                           test_db_session):
    _register(client)
    for slug in (L1_SLUG, "debits-and-credits", "journal-entries"):
        _lesson, detail = _lesson_by_slug(client, slug)
        for q in detail["questions"]:
            stored, _correct = _stored_keys(test_db_session, q["id"])
            assert [a["option_key"] for a in q["answers"]] == stored, (
                "%s question %s was reordered — only Lesson 2 may be"
                % (slug, q["id"])
            )
    assert L1_SLUG not in _OPTION_ORDER_LESSON_SLUGS
    assert SLUG in _OPTION_ORDER_LESSON_SLUGS


def test_lesson1_integrity_safeguards_unchanged(client, test_db_session):
    """Lesson 1 keeps its 18 unique ids/positions, correct-first grading and
    the same review-to-mastery behaviour."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, L1_SLUG)
    qs = detail["questions"]
    assert len(qs) == 18
    assert len({q["id"] for q in qs}) == 18
    assert [q["position"] for q in qs] == list(range(1, 19))
    assert detail["progress"]["questions_total"] == 18
    for q in qs:  # every question keeps its seeded option order, verbatim
        stored, correct = _stored_keys(test_db_session, q["id"])
        assert stored == [a["option_key"] for a in q["answers"]]
        if q["kind"] == "mcq":
            assert stored == sorted(stored)   # seeded A, B, C[, D] order
            assert correct in stored          # exactly one stored key is right
        else:
            assert stored == []               # short answers expose nothing
    # Grading semantics are untouched: submitting a question's stored correct
    # option_key still scores correct, and any other option_key still fails.
    probe = qs[0]
    correct0, wrong0 = _answer_keys(test_db_session, probe["id"])
    assert _attempt(client, lesson["id"], probe["id"],
                    option_key=correct0)["is_correct"] is True
    assert _attempt(client, lesson["id"], probe["id"],
                    option_key=wrong0)["is_correct"] is False

    for q in qs:  # all correct except position 3
        if q["position"] == 3:
            _c, w = _answer_keys(test_db_session, q["id"])
            _attempt(client, lesson["id"], q["id"], option_key=w)
        else:
            _attempt(client, lesson["id"], q["id"],
                     **_correct_answer_payload(test_db_session, q))
    progress = _lesson_by_slug(client, L1_SLUG)[1]["progress"]
    assert (progress["questions_answered"], progress["questions_correct"]) == (18, 17)
    assert progress["best_score"] == 94

    # Pick the position-3 card by question id (the grading probe above
    # deliberately left its own card on position 1).
    missed = next(q for q in qs if q["position"] == 3)
    card = next(c for c in _reviews(client)
                if c["question_id"] == missed["id"])
    correct, _w = _answer_keys(test_db_session, missed["id"])
    assert _answer_review(client, card["id"], option_key=correct)["correct"] is True
    progress = _lesson_by_slug(client, L1_SLUG)[1]["progress"]
    assert progress["questions_correct"] == 18
    assert progress["best_score"] == 100
    assert client.post("/learning/certificate").status_code == 403
