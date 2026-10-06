"""Lesson 5 expansion tests.

The original 2-section / 2-question Lesson 5 was expanded IN PLACE into a
complete beginner lesson (10 sections + 14 questions, all built around the
continuing "Manka'a Provisions" shop in Bamenda) WITHOUT creating a duplicate
lesson, course, slug, id or curriculum path: same slug ("journal-to-ledger"),
same curriculum position (5), same EN/FR titles, and the two ORIGINAL questions
keep their positions (1, 2), question ids, answer ids, option keys, correct
answers, explanations and corrections. Lesson 5 carries NO practice connector.

These tests pin:
1. Identity: slug/position/titles, the 7-lesson curriculum order, no duplicate.
2. Originals: positions 1-2 keep kind, option keys, correct answers, texts.
3. Persisted shape: 10 sections, 14 questions, unique ids, contiguous 1..14.
4. Seed/upsert idempotency + history preservation (double re-sync changes no
   question id, no answer id, no attempt/progress/review).
5. No duplicate normal sequence, no adjacent duplicate questions.
6. Wrong answer -> C1 remediation + C2 review card -> NEXT DISTINCT question.
7. Refresh/resume, bounded progress, review -> mastery on the SAME question id.
8. Stable answer-identity grading + safe deterministic option display, Lesson
   and Review using an identical order.
9. No connector on Lesson 5; Lesson 4 connector + Lessons 1-4 invariants intact.
10. Certificate rule `status == "completed" AND best_score == 100` unchanged.
"""
from app.learning.service import (
    _MEANINGFUL_OPTION_ORDER,
    _OPTION_ORDER_LESSON_SLUGS,
)
from app.models.learning import Answer, Attempt, Lesson, Question, ReviewItem
from app.services import certificate_service
from app.tests.test_learning import (
    EXPECTED_SLUGS,
    _answer_keys,
    _attempt,
    _correct_answer_payload,
    _lesson_by_slug,
    _register,
)
from app.tests.test_learning_reviews import _answer_review, _reviews

SLUG = "journal-to-ledger"

EXPECTED_KINDS = {
    1: "mcq", 2: "short_answer", 3: "mcq", 4: "mcq",
    5: "short_answer", 6: "mcq", 7: "mcq", 8: "mcq",
    9: "mcq", 10: "mcq", 11: "mcq", 12: "mcq",
    13: "mcq", 14: "mcq",
}

EXPECTED_REMEDIATION = {
    1: 2, 2: 3, 3: 3, 4: 4, 5: 5, 6: 5, 7: 6,
    8: 6, 9: 7, 10: 7, 11: 7, 12: 8, 13: 9, 14: 10,
}


def _stored_keys(session, question_id):
    """([stored option_keys in position order], correct option_key or None)."""
    rows = (
        session.query(Answer)
        .filter(Answer.question_id == question_id)
        .order_by(Answer.position)
        .all()
    )
    correct = next((a.option_key for a in rows if a.is_correct), None)
    return [a.option_key for a in rows], correct


def _displayed_keys(detail):
    return {
        q["id"]: [a["option_key"] for a in q["answers"]] for q in detail["questions"]
    }


# --- 1) Identity + curriculum order + no duplicate lesson ----------------------
def test_identity_curriculum_order_and_no_duplicate_lesson(client, test_db_session):
    _register(client)
    lessons = client.get("/learning/lessons").json()
    assert [l["slug"] for l in lessons] == EXPECTED_SLUGS
    assert [l["position"] for l in lessons] == [1, 2, 3, 4, 5, 6, 7]
    assert len([l for l in lessons if l["slug"] == SLUG]) == 1
    lesson = lessons[4]
    assert lesson["position"] == 5
    assert lesson["title_en"] == "From journal to ledger"
    assert lesson["title_fr"] == "Du journal au grand livre"
    assert lesson["title_en"] != lesson["title_fr"]
    assert lesson["summary_en"] and lesson["summary_fr"]
    rows = test_db_session.query(Lesson).filter(Lesson.slug == SLUG).all()
    assert len(rows) == 1
    assert len({l["id"] for l in lessons}) == 7
    assert certificate_service.COURSE_SLUG == "accounting-basics"


# --- 2) Original questions/answers preserved, no connector ---------------------
def test_original_questions_answers_preserved_and_no_connector(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    q1, q2 = qs[0], qs[1]
    assert (q1["position"], q1["kind"]) == (1, "mcq")
    assert "ledger" in q1["question_en"].lower()
    rows1 = (
        test_db_session.query(Answer)
        .filter(Answer.question_id == q1["id"])
        .order_by(Answer.position)
        .all()
    )
    assert [a.option_key for a in rows1] == ["A", "B", "C"]
    assert [a.is_correct for a in rows1] == [True, False, False]
    assert (q2["position"], q2["kind"]) == (2, "short_answer")
    assert "individual ledger account" in q2["question_en"]
    row2 = test_db_session.get(Question, q2["id"])
    assert row2.short_answer_en == "account"
    assert row2.short_answer_fr == "compte"
    assert row2.posts_demo_transaction is False
    assert not any(q["posts_demo_transaction"] for q in qs)


# --- 3) Persisted shape: 10 sections, 14 questions, contiguous positions ------
def test_lesson5_has_10_sections_and_14_unique_positions(client):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    secs, qs = detail["sections"], detail["questions"]
    assert len(secs) == 10
    assert [s["position"] for s in secs] == list(range(1, 11))
    assert len(qs) == 14
    assert len({q["id"] for q in qs}) == 14
    assert [q["position"] for q in qs] == list(range(1, 15))
    for a, b in zip(qs, qs[1:]):
        assert a["id"] != b["id"]
        assert a["position"] != b["position"]
        assert a["question_en"] != b["question_en"]
        assert a["question_fr"] != b["question_fr"]
    assert {q["position"]: q["kind"] for q in qs} == EXPECTED_KINDS
    assert detail["progress"]["questions_total"] == 14
    for q in qs:
        assert "is_correct" not in q
        for a in q["answers"]:
            assert "is_correct" not in a


# --- 4) EN/FR parity, explanations, corrections, remediation links ------------
def test_bilingual_content_feedback_and_remediation_links(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    for s in detail["sections"]:
        assert s["heading_en"] and s["heading_fr"]
        assert s["body_en"] and s["body_fr"]
        assert s["body_en"] != s["body_fr"]
    for q in detail["questions"]:
        assert q["question_en"] and q["question_fr"]
        assert q["question_en"] != q["question_fr"]
        row = test_db_session.get(Question, q["id"])
        assert row.explanation_en and row.explanation_fr
        assert row.correction_en and row.correction_fr
        assert row.explanation_en != row.explanation_fr
        assert row.correction_en != row.correction_fr
        if q["kind"] == "mcq":
            assert len(q["answers"]) >= 2
            for a in q["answers"]:
                assert a["text_en"] and a["text_fr"]
                assert a["text_en"] != a["text_fr"]
        else:
            assert q["answers"] == []
    positions = {s["position"] for s in detail["sections"]}
    for q in detail["questions"]:
        row = test_db_session.get(Question, q["id"])
        assert row.remediation_section_id is not None
        target = next(
            s for s in detail["sections"] if s["id"] == row.remediation_section_id
        )
        assert target["position"] == EXPECTED_REMEDIATION[q["position"]]
        assert target["position"] in positions
    bodies_en = "\n".join(s["body_en"] for s in detail["sections"])
    bodies_fr = "\n".join(s["body_fr"] for s in detail["sections"])
    for needle in ("BEFORE YOU START", "Manka'a Provisions",
                   "AN HONEST PROMISE", "0110", "F-221", "BS-12"):
        assert needle in bodies_en, needle
    for needle in ("AVANT DE COMMENCER", "Manka'a Provisions",
                   "UNE PROMESSE HONNETE", "0110", "F-221", "BS-12"):
        assert needle in bodies_fr, needle
    forbidden = ("you are now an accountant", "certified accountant",
                 "chartered accountant")
    whole = (bodies_en + " " + bodies_fr).lower()
    for phrase in forbidden:
        assert phrase not in whole, phrase

# --- 5) Seed/upsert idempotency + history preserved ---------------------------
def test_reseed_is_idempotent_and_preserves_all_history(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    wrong_q = qs[4]  # position 5
    _attempt(client, lesson["id"], wrong_q["id"],
             option_key=_answer_keys(test_db_session, wrong_q["id"])[1])
    for q in qs:
        if q["position"] == 5:
            continue
        _attempt(client, lesson["id"], q["id"],
                 **_correct_answer_payload(test_db_session, q))
    q_ids = {q["position"]: q["id"] for q in qs}
    a_ids = {
        q["position"]: {a.id for a in
                        test_db_session.query(Answer)
                        .filter(Answer.question_id == q["id"]).all()}
        for q in qs
    }
    attempts_before = {
        a.id: (a.question_id, a.is_correct, a.selected_answer_id)
        for a in test_db_session.query(Attempt).all()
    }
    cards_before = {(c.question_id, c.stage) for c in test_db_session.query(ReviewItem).all()}
    progress_before = _lesson_by_slug(client, SLUG)[1]["progress"]
    for _ in range(3):
        _lesson_by_slug(client, SLUG)
        client.get("/learning/lessons")
    lesson2, detail2 = _lesson_by_slug(client, SLUG)
    assert lesson2["id"] == lesson["id"]
    assert {q["position"]: q["id"] for q in detail2["questions"]} == q_ids
    for q in detail2["questions"]:
        now = {a.id for a in test_db_session.query(Answer)
               .filter(Answer.question_id == q["id"]).all()}
        assert now == a_ids[q["position"]], q["position"]
    assert len(detail2["questions"]) == 14
    assert len(detail2["sections"]) == 10
    attempts_after = {
        a.id: (a.question_id, a.is_correct, a.selected_answer_id)
        for a in test_db_session.query(Attempt).all()
    }
    assert attempts_after == attempts_before
    assert {(c.question_id, c.stage) for c in test_db_session.query(ReviewItem).all()} == cards_before
    assert _lesson_by_slug(client, SLUG)[1]["progress"] == progress_before


# --- 6) Wrong answer -> remediation + review -> NEXT DISTINCT question --------
def test_wrong_answer_remediation_review_and_next_distinct_question(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    missed = qs[4]  # position 5
    res = _attempt(client, lesson["id"], missed["id"],
                   option_key=_answer_keys(test_db_session, missed["id"])[1])
    assert res["is_correct"] is False
    fb = res["feedback"]
    assert fb["correct"] is False
    assert fb["explanation"] and fb["correction"]
    rem = fb["remediation"]
    assert rem is not None and rem["lesson_id"] == lesson["id"]
    assert rem["section_position"] == EXPECTED_REMEDIATION[5]
    cards = _reviews(client)
    assert len(cards) == 1
    assert cards[0]["question_id"] == missed["id"]
    assert cards[0]["is_due"] is True
    detail2 = _lesson_by_slug(client, SLUG)[1]
    assert [x["id"] for x in detail2["questions"]] == [x["id"] for x in qs]
    nxt = detail2["questions"][5]
    assert nxt["id"] != missed["id"]
    assert nxt["position"] == missed["position"] + 1
    _attempt(client, lesson["id"], missed["id"],
             option_key=_answer_keys(test_db_session, missed["id"])[1])
    detail3 = _lesson_by_slug(client, SLUG)[1]
    assert [x["id"] for x in detail3["questions"]] == [x["id"] for x in qs]
    assert len({c["question_id"] for c in _reviews(client)}) == 1


# --- 7) Refresh/resume, bounded progress, review -> mastery -------------------
def test_progress_bounded_and_review_correction_updates_same_question(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    missed = qs[9]  # position 10
    for q in qs:
        if q["position"] == 10:
            _attempt(client, lesson["id"], q["id"],
                     option_key=_answer_keys(test_db_session, q["id"])[1])
        else:
            _attempt(client, lesson["id"], q["id"],
                     **_correct_answer_payload(test_db_session, q))
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert p["questions_total"] == 14
    assert p["questions_answered"] == 14
    assert p["questions_correct"] == 13
    assert p["best_score"] == 93
    assert p["status"] == "completed"
    _attempt(client, lesson["id"], missed["id"],
             **_correct_answer_payload(test_db_session, missed))
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert p["questions_answered"] == 14
    assert p["questions_correct"] == 14
    assert p["best_score"] == 100
    card = next(c for c in _reviews(client) if c["question_id"] == missed["id"])
    before = {a.id for a in test_db_session.query(Attempt).all()}
    out = _answer_review(client, card["id"],
                         **_correct_answer_payload(test_db_session, missed))
    assert out["correct"] is True
    new_rows = [a for a in test_db_session.query(Attempt).all() if a.id not in before]
    assert len(new_rows) == 1
    assert new_rows[0].question_id == missed["id"]
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert p["questions_answered"] == 14
    assert p["questions_correct"] == 14
    assert p["best_score"] == 100
    again = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert again == p


# --- 8) Stable answer-identity grading + safe deterministic option display ----
def test_stable_grading_and_deterministic_option_display(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    assert SLUG in _OPTION_ORDER_LESSON_SLUGS
    exempt = _MEANINGFUL_OPTION_ORDER.get(SLUG, frozenset())
    assert exempt == frozenset()
    baseline = _displayed_keys(detail)
    positions = []
    for q in detail["questions"]:
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == q["id"])
            .all()
        )
        assert len({a.id for a in rows}) == len(rows)
        if q["kind"] != "mcq":
            assert rows == []
            continue
        assert len(rows) >= 2
        assert sum(1 for a in rows if a.is_correct) == 1
        assert sorted(baseline[q["id"]]) == sorted(a.option_key for a in rows)
        if q["position"] not in exempt:
            positions.append(
                baseline[q["id"]].index(
                    next(a.option_key for a in rows if a.is_correct)
                )
            )
    assert positions and max(positions) > 0
    assert len(set(positions)) > 1
    for _ in range(3):
        assert _displayed_keys(_lesson_by_slug(client, SLUG)[1]) == baseline
    fr = client.get("/learning/lessons/%d?lang=fr" % lesson["id"]).json()
    assert _displayed_keys(fr) == baseline
    mcqs = [q for q in detail["questions"] if q["kind"] == "mcq"]
    shorts = [q for q in detail["questions"] if q["kind"] == "short_answer"]
    sample = [mcqs[0], mcqs[-1]] + shorts[:1]
    for q in sample:
        payload = _correct_answer_payload(test_db_session, q)
        assert _attempt(client, lesson["id"], q["id"],
                        **payload)["is_correct"] is True
        if q["kind"] == "mcq":
            wrong = _answer_keys(test_db_session, q["id"])[1]
            assert _attempt(client, lesson["id"], q["id"],
                            option_key=wrong)["is_correct"] is False
    assert _displayed_keys(_lesson_by_slug(client, SLUG)[1]) == baseline
    assert _displayed_keys(
        client.get("/learning/lessons/%d?lang=fr" % lesson["id"]).json()
    ) == baseline


# --- 9) Review queue renders the SAME deterministic option order --------------
def test_review_uses_identical_deterministic_option_order(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    baseline = _displayed_keys(detail)
    probe = next(q for q in detail["questions"] if q["kind"] == "mcq" and q["position"] > 1)
    _attempt(client, lesson["id"], probe["id"],
             option_key=_answer_keys(test_db_session, probe["id"])[1])
    card = next(c for c in _reviews(client) if c["question_id"] == probe["id"])
    assert [a["option_key"] for a in card["answers"]] == baseline[probe["id"]]
    _answer_review(client, card["id"],
                   option_key=_answer_keys(test_db_session, probe["id"])[1])
    card2 = next(c for c in _reviews(client) if c["question_id"] == probe["id"])
    assert [a["option_key"] for a in card2["answers"]] == baseline[probe["id"]]


# --- 10) No connector on Lesson 5 + Lessons 1-4 invariants --------------------
def test_no_connector_and_lessons_1_to_4_invariants(client, test_db_session):
    _register(client)
    _lesson5, l5 = _lesson_by_slug(client, SLUG)
    assert not any(q["posts_demo_transaction"] for q in l5["questions"])
    for slug, total in (("what-is-accounting", 18), ("the-accounting-equation", 18),
                        ("debits-and-credits", 18), ("journal-entries", 18)):
        _lesson, detail = _lesson_by_slug(client, slug)
        qs = detail["questions"]
        assert len(qs) == total
        assert len({q["id"] for q in qs}) == total
        assert [q["position"] for q in qs] == list(range(1, total + 1))
        assert detail["progress"]["questions_total"] == total
        if slug in ("the-accounting-equation", "debits-and-credits", "journal-entries"):
            assert slug in _OPTION_ORDER_LESSON_SLUGS
        else:
            assert slug not in _OPTION_ORDER_LESSON_SLUGS
    _lesson4, l4 = _lesson_by_slug(client, "journal-entries")
    flagged = [q for q in l4["questions"] if q["posts_demo_transaction"]]
    assert len(flagged) == 1 and flagged[0]["position"] == 1


# --- 11) Certificate rule unchanged -------------------------------------------
def test_certificate_rule_unchanged_after_expansion(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    for q in detail["questions"]:
        _attempt(client, lesson["id"], q["id"],
                 **_correct_answer_payload(test_db_session, q))
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert p["status"] == "completed"
    assert p["best_score"] == 100
    completion = client.get("/learning/completion").json()
    assert completion["total_lessons"] == 7
    assert completion["completed_lessons"] == 1
    assert completion["completed"] is False
    assert completion["certificate_status"] == "locked"
    assert client.post("/learning/certificate").status_code == 403


