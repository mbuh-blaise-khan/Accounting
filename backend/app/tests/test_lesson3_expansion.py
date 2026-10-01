"""Lesson 3 expansion tests.

The original 3-question/3-section Lesson 3 was expanded IN PLACE into a full
beginner lesson (10 sections + 18 questions, all built around the continuing
"Manka'a Provisions" scenario in Bamenda) WITHOUT touching the engine: same
slug ("debits-and-credits"), same curriculum position (3), and the three
ORIGINAL questions keep their positions (1, 2, 3), question ids, answer ids,
option keys, correct answers and accepted short-answer texts.

These tests pin:
1. Identity: slug/position and the 7-lesson curriculum order are unchanged.
2. Originals: positions 1-3 keep kind, option keys, correct answers, accepted
   texts, and their stored answer records survive re-sync.
3. Seed + persisted shape: 10 sections, 18 questions, unique immutable ids,
   unique contiguous positions, EN/FR content everywhere.
4. History preservation: a double re-sync changes no question id, no answer id
   and no learner attempt/progress.
5. Remediation (C1): every question's stored pointer resolves to a section of
   THIS lesson, in EN and FR.
6. Wrong answer -> remediation + review card, next DISTINCT question, the
   normal sequence unchanged (no duplicates).
7. Review correction updates mastery for the SAME immutable question id.
8. Progress is bounded by the fixed total and counts distinct questions.
9. Option presentation is deterministic and does not reveal the correct slot;
   grading is by stable option key, never display index.
10. Certificate: one completed lesson leaves the course locked, and the rule is
    still `status == "completed" AND best_score == 100`.
11. Lesson 1 and Lesson 2 regression invariants.
"""
from collections import Counter

from app.learning.service import (
    _MEANINGFUL_OPTION_ORDER,
    _OPTION_ORDER_LESSON_SLUGS,
)
from app.models.learning import Answer, Attempt, Question
from app.tests.test_learning import (
    EXPECTED_SLUGS,
    _answer_keys,
    _attempt,
    _correct_answer_payload,
    _lesson_by_slug,
    _register,
)
from app.tests.test_learning_reviews import _answer_review, _reviews

SLUG = "debits-and-credits"

EXPECTED_KINDS = {
    1: "mcq", 2: "mcq", 3: "short_answer",
    **{p: "mcq" for p in range(4, 16)},
    16: "short_answer", 17: "mcq", 18: "mcq",
}

EXPECTED_REMEDIATION = {
    1: 2, 2: 3, 3: 2, 4: 4, 5: 5, 6: 4, 7: 4, 8: 3, 9: 5, 10: 6,
    11: 5, 12: 2, 13: 8, 14: 9, 15: 9, 16: 2, 17: 6, 18: 10,
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
# --- 1) Identity + curriculum order ------------------------------------------
def test_identity_and_curriculum_order_unchanged(client):
    _register(client)
    lessons = client.get("/learning/lessons").json()
    assert [l["slug"] for l in lessons] == EXPECTED_SLUGS
    assert [l["position"] for l in lessons] == [1, 2, 3, 4, 5, 6, 7]
    lesson = next(l for l in lessons if l["slug"] == SLUG)
    assert lesson["position"] == 3
    assert lesson["title_en"] == "Debits and credits"
    assert lesson["title_fr"] == "Le débit et le crédit"
    assert lesson["title_en"] != lesson["title_fr"]
    assert lesson["summary_en"] and lesson["summary_fr"]
    assert lesson["progress"]["status"] == "not_started"
    assert lesson["progress"]["questions_total"] == 18


# --- 2) The three original questions are preserved ---------------------------
def test_original_three_questions_preserved(client, test_db_session):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    q1, q2, q3 = qs[0], qs[1], qs[2]
    # Q1 — cash sale, mcq, option-key SET unchanged; stored rows unchanged.
    assert (q1["kind"], q1["position"]) == ("mcq", 1)
    assert "30,000" in q1["question_en"] and "30 000" in q1["question_fr"]
    assert {a["option_key"] for a in q1["answers"]} == {"A", "B", "C"}
    rows1 = (
        test_db_session.query(Answer)
        .filter(Answer.question_id == q1["id"])
        .order_by(Answer.position)
        .all()
    )
    assert [a.option_key for a in rows1] == ["A", "B", "C"]
    assert [a.is_correct for a in rows1] == [True, False, False]
    # Q2 — "ALWAYS true", mcq, A correct.
    assert (q2["kind"], q2["position"]) == ("mcq", 2)
    assert "ALWAYS" in q2["question_en"] and "TOUJOURS" in q2["question_fr"]
    correct2, _w2 = _answer_keys(test_db_session, q2["id"])
    assert correct2 == "A"
    # Q3 — still the FIRST short answer in served order, texts unchanged.
    shorts = [q for q in qs if q["kind"] == "short_answer"]
    assert shorts[0]["position"] == 3
    assert (q3["kind"], q3["position"]) == ("short_answer", 3)
    row3 = test_db_session.get(Question, q3["id"])
    assert row3.short_answer_en == "debited"
    assert row3.short_answer_fr == "débitée"


# --- 3) Seed + persisted shape: unique ids and contiguous positions ----------
def test_lesson3_has_10_sections_and_18_unique_positions(client):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    secs = detail["sections"]
    qs = detail["questions"]
    assert len(secs) == 10
    assert [s["position"] for s in secs] == list(range(1, 11))
    assert len(qs) == 18
    ids = [q["id"] for q in qs]
    assert len(set(ids)) == 18  # each immutable id exactly once
    positions = [q["position"] for q in qs]
    assert positions == list(range(1, 19))  # unique + contiguous + ordered
    for a, b in zip(qs, qs[1:]):
        assert a["id"] != b["id"]
        assert a["position"] != b["position"]
        assert a["question_en"] != b["question_en"]
        assert a["question_fr"] != b["question_fr"]
    assert {q["position"]: q["kind"] for q in qs} == EXPECTED_KINDS


# --- 4) EN/FR content completeness ------------------------------------------
def test_content_completeness_bilingual(client, test_db_session):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
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
        if q["kind"] == "mcq":
            assert len(q["answers"]) >= 2
            for a in q["answers"]:
                assert a["text_en"] and a["text_fr"]
                assert a["text_en"] != a["text_fr"]
        else:
            assert q["answers"] == []
    bodies = "\n".join(s["body_en"] for s in detail["sections"])
    corps = "\n".join(s["body_fr"] for s in detail["sections"])
    for needle in ("By the end of this lesson", "BEFORE YOU START",
                   "Manka'a Provisions", "Nkwen Market", "Mama Ndifor",
                   "Mobile Money", "323,000", "Dr Cash", "Dr Stock"):
        assert needle in bodies, needle
    for needle in ("À la fin de cette leçon", "AVANT DE COMMENCER",
                   "Manka'a Provisions", "Nkwen Market", "Mama Ndifor",
                   "Mobile Money", "323 000", "Dr Trésorerie", "Dr Stocks"):
        assert needle in corps, needle
    ref_en = detail["sections"][9]["body_en"]
    ref_fr = detail["sections"][9]["body_fr"]
    for needle in ("OHADA", "ifrs.org", "ONECCA", "OPTIONAL ACADEMIC READING",
                   "NO UBa endorsement", "does NOT make you an accountant"):
        assert needle in ref_en, needle
    for needle in ("OHADA", "ifrs.org", "ONECCA",
                   "LECTURES ACADÉMIQUES OPTIONNELLES",
                   "AUCUNE caution de l'UBa", "ne fait PAS de vous un comptable"):
        assert needle in ref_fr, needle


# --- 5) Idempotent repeat seed/upsert ----------------------------------------
def test_repeat_resync_preserves_ids_attempts_and_progress(
    client, test_db_session
):
    """A DOUBLE re-sync adds no rows and changes no question/answer id."""
    from app.learning.service import ensure_default_lessons

    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    ids_before = [q["id"] for q in qs]
    aids_before = {
        q["id"]: [a.id for a in (
            test_db_session.query(Answer)
            .filter(Answer.question_id == q["id"])
            .order_by(Answer.position).all())]
        for q in qs
    }

    # One correct answer on a new question, one wrong on an original.
    q11 = qs[10]
    assert _attempt(client, lesson["id"], q11["id"],
                    **_correct_answer_payload(test_db_session, q11))["is_correct"]
    q1 = qs[0]
    _c1, w1 = _answer_keys(test_db_session, q1["id"])
    assert _attempt(client, lesson["id"], q1["id"], option_key=w1)["is_correct"] is False
    before = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert before["questions_answered"] == 2
    assert before["questions_total"] == 18
    assert before["status"] == "in_progress"

    for _ in range(2):  # double seed must not duplicate anything
        ensure_default_lessons(test_db_session)
        test_db_session.commit()
    test_db_session.expire_all()

    detail2 = _lesson_by_slug(client, SLUG)[1]
    assert [q["id"] for q in detail2["questions"]] == ids_before
    assert [q["position"] for q in detail2["questions"]] == list(range(1, 19))
    assert len({q["id"] for q in detail2["questions"]}) == 18
    for q in detail2["questions"]:
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == q["id"])
            .order_by(Answer.position).all()
        )
        assert [a.id for a in rows] == aids_before[q["id"]]
    assert detail2["progress"] == before
    assert test_db_session.query(Attempt).count() == 2


# --- 6) C1 remediation resolves inside THIS lesson, EN + FR -----------------
def test_remediation_targets_are_this_lessons_own_sections(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    section_ids = {s["id"] for s in detail["sections"]}
    by_pos = {q["position"]: q for q in detail["questions"]}
    for pos, sec_pos in EXPECTED_REMEDIATION.items():
        q = by_pos[pos]
        if q["kind"] == "mcq":
            _c, wrong = _answer_keys(test_db_session, q["id"])
            res = _attempt(client, lesson["id"], q["id"], option_key=wrong)
        else:
            res = _attempt(client, lesson["id"], q["id"], text="not the answer")
        assert res["is_correct"] is False, pos
        rem = res["feedback"]["remediation"]
        assert rem is not None, pos
        assert rem["lesson_id"] == lesson["id"], pos
        assert rem["section_id"] in section_ids, pos
        assert rem["section_position"] == sec_pos, pos
    # French feedback localizes the remediation label and the section title.
    q5 = by_pos[5]
    _c5, w5 = _answer_keys(test_db_session, q5["id"])
    fr = _attempt(client, lesson["id"], q5["id"], lang="fr", option_key=w5)
    rem_fr = fr["feedback"]["remediation"]
    sec5 = next(s for s in detail["sections"] if s["position"] == 5)
    assert rem_fr["section_position"] == 5
    assert rem_fr["section_title"] == sec5["heading_fr"]


# --- 7) Wrong answer -> remediation + review, next DISTINCT question --------
def test_wrong_answer_schedules_review_and_advances_distinctly(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    q3 = qs[2]  # position 3, the original short answer
    res = _attempt(client, lesson["id"], q3["id"], text="credited")
    assert res["is_correct"] is False
    fb = res["feedback"]
    assert fb["correct"] is False
    assert fb["explanation"] and fb["correction"]
    assert fb["remediation"] is not None  # C1 still offered

    cards = _reviews(client)
    assert len(cards) == 1
    assert cards[0]["question_id"] == q3["id"]
    assert cards[0]["lesson_id"] == lesson["id"]
    assert cards[0]["is_due"] is True

    # The normal sequence is byte-identical — no re-insert, no reorder.
    detail2 = _lesson_by_slug(client, SLUG)[1]
    assert [x["id"] for x in detail2["questions"]] == [x["id"] for x in qs]
    nxt = detail2["questions"][3]
    assert nxt["id"] != q3["id"]           # next question is DISTINCT
    assert nxt["position"] == q3["position"] + 1  # counter moves on exactly +1


# --- 8) Review correction updates mastery for the SAME question id ----------
def test_review_correction_updates_mastery_for_same_question_id(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    by_pos = {q["position"]: q for q in qs}
    q3 = by_pos[3]
    # Answer everything correctly EXCEPT position 3, which is answered wrong.
    for q in qs:
        if q["position"] == 3:
            _attempt(client, lesson["id"], q["id"], text="credited")
        else:
            _attempt(client, lesson["id"], q["id"],
                     **_correct_answer_payload(test_db_session, q))
    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_total"] == 18
    assert progress["questions_answered"] == 18
    assert progress["questions_correct"] == 17
    assert progress["best_score"] == 94          # round(17 / 18 * 100)
    assert progress["status"] == "completed"     # every question visited

    card = next(c for c in _reviews(client)
                if c["question_id"] == q3["id"])
    attempts_before = {a.id for a in test_db_session.query(Attempt).all()}
    res = _answer_review(client, card["id"], text="debited")
    assert res["correct"] is True
    new_rows = [a for a in test_db_session.query(Attempt).all()
                if a.id not in attempts_before]
    assert len(new_rows) == 1
    assert new_rows[0].question_id == q3["id"]   # SAME immutable question id

    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_correct"] == 18
    assert progress["best_score"] == 100
    assert progress["status"] == "completed"


# --- 9) Progress is bounded by the fixed total ------------------------------
def test_progress_counts_distinct_questions_and_never_exceeds_total(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    q5 = qs[4]
    c5, w5 = _answer_keys(test_db_session, q5["id"])
    # Several retries on ONE question must not inflate the count.
    for key in (w5, c5, w5, c5, c5):
        _attempt(client, lesson["id"], q5["id"], option_key=key)
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert p["questions_answered"] == 1        # ONE distinct question
    assert p["questions_correct"] == 1         # latest attempt is correct
    assert p["questions_answered"] <= p["questions_total"] == 18
    assert p["status"] == "in_progress"        # retries never fake completion
    # Now walk the WHOLE fixed sequence; position 5 is re-answered on purpose
    # (a retry, not a new question).
    for q in qs:
        _attempt(client, lesson["id"], q["id"],
                 **_correct_answer_payload(test_db_session, q))
        p = _lesson_by_slug(client, SLUG)[1]["progress"]
        assert p["questions_answered"] <= p["questions_total"]  # bounded always
    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_answered"] == 18
    assert progress["questions_correct"] == 18
    assert progress["status"] == "completed"
    assert progress["best_score"] == 100


# --- 10) Refresh / resume resumes from authoritative persisted progress ------
def test_refresh_and_resume_resume_from_persisted_progress(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    for q in qs[:5]:
        _attempt(client, lesson["id"], q["id"],
                 **_correct_answer_payload(test_db_session, q))
    for _ in range(3):  # simulate refresh / navigate away-and-back
        again = _lesson_by_slug(client, SLUG)[1]
        assert [x["id"] for x in again["questions"]] == [x["id"] for x in qs]
        assert [x["position"] for x in again["questions"]] == list(range(1, 19))
        assert again["progress"]["questions_answered"] == 5
        assert again["progress"]["questions_total"] == 18
        assert again["progress"]["status"] == "in_progress"


# --- 11) Option presentation + grading by answer identity -------------------
def test_option_display_order_deterministic_and_does_not_reveal_answer(
    client, test_db_session
):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    assert SLUG in _OPTION_ORDER_LESSON_SLUGS
    exempt = _MEANINGFUL_OPTION_ORDER.get(SLUG, frozenset())
    positions = []
    for q in detail["questions"]:
        if q["kind"] != "mcq" or q["position"] in exempt:
            continue
        _keys, correct = _stored_keys(test_db_session, q["id"])
        served = [a["option_key"] for a in q["answers"]]
        assert len(set(served)) == len(served)  # unique keys
        assert set(served) == set(_keys)        # same options as stored
        positions.append(served.index(correct) + 1)
    assert positions
    # The correct answer must not be systematically in one visible slot.
    assert len(set(positions)) >= 2, positions
    assert set(positions) == {1, 2, 3}, positions
    top = Counter(positions).most_common(1)[0][1]
    assert top <= max(2, (len(positions) * 2) // 3)


def test_option_display_order_stable_and_grading_by_answer_key(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)

    def keys_map(d):
        return {q["id"]: [a["option_key"] for a in q["answers"]]
                for q in d["questions"]}

    baseline = keys_map(detail)
    for _ in range(3):  # re-fetch / refresh / navigate away-and-back
        assert keys_map(_lesson_by_slug(client, SLUG)[1]) == baseline
    fr = client.get("/learning/lessons/%d?lang=fr" % lesson["id"]).json()
    assert keys_map(fr) == baseline  # EN/FR render the SAME order

    q = next(x for x in detail["questions"] if x["kind"] == "mcq")
    correct, wrong = _answer_keys(test_db_session, q["id"])
    # Grading is by the stable option key, never the display index.
    assert _attempt(client, lesson["id"], q["id"],
                    option_key=correct)["is_correct"] is True
    assert _attempt(client, lesson["id"], q["id"],
                    option_key=wrong)["is_correct"] is False
    # Display order is untouched by answering.
    assert keys_map(_lesson_by_slug(client, SLUG)[1]) == baseline


# --- 12) Certificate rule unchanged -------------------------------------------
def test_certificate_rule_and_completion_unchanged(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    for q in detail["questions"]:
        _attempt(client, lesson["id"], q["id"],
                 **_correct_answer_payload(test_db_session, q))
    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    # The rule is exactly: status == "completed" AND best_score == 100.
    assert progress["status"] == "completed"
    assert progress["best_score"] == 100
    completion = client.get("/learning/completion").json()
    assert completion["total_lessons"] == 7
    assert completion["completed_lessons"] == 1
    assert completion["completed"] is False
    assert completion["certificate_status"] == "locked"
    assert client.post("/learning/certificate").status_code == 403


# --- 13) Lesson 1 + Lesson 2 regression invariants --------------------------
def test_lesson1_and_lesson2_regression_invariants(client, test_db_session):
    _register(client)
    for slug in ("what-is-accounting", "the-accounting-equation"):
        lesson, detail = _lesson_by_slug(client, slug)
        qs = detail["questions"]
        assert len(qs) == 18
        assert len({q["id"] for q in qs}) == 18
        assert [q["position"] for q in qs] == list(range(1, 19))
        assert detail["progress"]["questions_total"] == 18
        # Progress / review / certificate behavior for each still works.
        for q in qs:  # answer all correctly
            _attempt(client, lesson["id"], q["id"],
                     **_correct_answer_payload(test_db_session, q))
        progress = _lesson_by_slug(client, slug)[1]["progress"]
        assert progress["questions_answered"] == 18
        assert progress["questions_correct"] == 18
        assert progress["status"] == "completed"
        assert progress["best_score"] == 100
    # Two lessons completed at once still leave the course locked: the rule
    # requires ALL SEVEN at status == "completed" AND best_score == 100.
    completion = client.get("/learning/completion").json()
    assert completion["total_lessons"] == 7
    assert completion["completed_lessons"] == 2
    assert completion["completed"] is False
    assert completion["certificate_status"] == "locked"
    assert client.post("/learning/certificate").status_code == 403


# __MORE__
