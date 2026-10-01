"""Lesson 2 expansion tests.

The original 3-question/3-section Lesson 2 was upgraded IN PLACE into a full
beginner lesson (10 sections + 18 questions — all built around the continuing
"Manka'a Provisions" scenario in Bamenda) WITHOUT touching the engine: same
slug ("the-accounting-equation"), same curriculum position (2), and the three
ORIGINAL questions keep their positions (1, 2, 3), question ids, answer ids,
option keys and accepted short-answer texts, so historical attempts, progress
rows, review cards, current mastery and certificate eligibility are all
preserved.

These tests pin, for the expanded content:
1. Identity: slug/position and the 7-lesson curriculum order are unchanged;
   Lesson 2 serves one unique row per immutable question id and one unique
   fixed position (1..18), with no adjacent duplicates.
2. Original questions: positions 1-3 keep kind, option keys, correct answers
   and accepted short-answer texts.
3. History preservation: question/answer ids are stable across re-sync
   (even a double sync) and attempts/progress rows survive it.
4. Scoring: correct/incorrect grading on the new questions including the
   short answers (accepted EN + FR, language-blind); best_score roll-up.
5. Content completeness: every requested beginner element is present in
   BOTH languages.
6. Remediation (C1): every question's target resolves to the intended
   section of the SAME lesson (deterministic position map), EN + FR.
7. Review compatibility (C2): a wrong answer creates a card without
   duplicating the normal sequence; a correct review answer updates mastery
   for the SAME immutable question id (Session 18 behavior).
8. Progress invariants: counts are distinct immutable question ids and can
   never exceed the denominator.
9. Certificate rule: the expanded lesson feeds course completion, and one
   completed lesson alone never unlocks the course certificate.
10. Lesson 1 regression guard: 18-question sequence, progress,
    review-to-mastery and certificate behavior unchanged.
11. Answer-key protection: read endpoints never leak key material.
"""
import json

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

SLUG = "the-accounting-equation"

# position of question -> position of the section its remediation points at
# (authored in the seed; must always resolve to a real section of THIS lesson).
EXPECTED_REMEDIATION = {
    1: 2, 2: 2, 3: 3, 4: 4, 5: 5, 6: 2, 7: 2, 8: 3, 9: 6,
    10: 4, 11: 5, 12: 6, 13: 8, 14: 9, 15: 7, 16: 2, 17: 3, 18: 10,
}

EXPECTED_KINDS = {
    1: "mcq", 2: "short_answer", 3: "mcq", 4: "mcq", 5: "mcq",
    6: "short_answer", 7: "mcq", 8: "mcq", 9: "mcq", 10: "mcq",
    11: "mcq", 12: "mcq", 13: "mcq", 14: "mcq", 15: "mcq",
    16: "short_answer", 17: "mcq", 18: "mcq",
}

# --- 1) Identity: slug/position and curriculum order -------------------------
def test_identity_and_curriculum_order_unchanged(client):
    _register(client)
    lessons = client.get("/learning/lessons").json()
    assert [l["slug"] for l in lessons] == EXPECTED_SLUGS
    assert [l["position"] for l in lessons] == [1, 2, 3, 4, 5, 6, 7]
    lesson = next(l for l in lessons if l["slug"] == SLUG)
    assert lesson["position"] == 2
    assert lesson["title_en"] == "The accounting equation"
    assert lesson["title_fr"] == "L'équation comptable"
    assert lesson["title_en"] != lesson["title_fr"]
    assert lesson["summary_en"] and lesson["summary_fr"]
    assert lesson["progress"]["status"] == "not_started"
    assert lesson["progress"]["questions_total"] == 18


# --- 2) Unique ids + fixed positions, no adjacent duplicates -----------------
def test_lesson2_has_18_unique_ids_and_positions(client):
    """One unique row per immutable question id, one unique position 1..18."""
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    ids = [q["id"] for q in qs]
    positions = [q["position"] for q in qs]
    assert len(qs) == 18
    assert len(set(ids)) == 18  # each immutable id exactly once
    assert positions == list(range(1, 19))  # each position exactly once
    for a, b in zip(qs, qs[1:]):  # no adjacent duplicates of any kind
        assert a["id"] != b["id"]
        assert a["position"] != b["position"]
        assert a["question_en"] != b["question_en"]
        assert a["question_fr"] != b["question_fr"]
    assert {q["position"]: q["kind"] for q in qs} == EXPECTED_KINDS


# --- 3) The three original questions are preserved ---------------------------
def test_original_three_questions_preserved(client, test_db_session):
    """Positions 1-3 keep kind, option keys, correct answers, accepted texts."""
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    q1, q2, q3 = detail["questions"][:3]
    assert (q1["kind"], q1["position"]) == ("mcq", 1)
    assert "200,000" in q1["question_en"] and "200 000" in q1["question_fr"]
    # The SET of option keys is unchanged. (Their DISPLAY order is a
    # deterministic function of the immutable answer ids — see the option-order
    # hotfix — so it is asserted in the option-order tests, not here.)
    assert {a["option_key"] for a in q1["answers"]} == {"A", "B", "C"}
    # ...and the STORED rows are still the original A/B/C, correct-first.
    stored1 = (
        test_db_session.query(Answer)
        .filter(Answer.question_id == q1["id"])
        .order_by(Answer.position)
        .all()
    )
    assert [a.option_key for a in stored1] == ["A", "B", "C"]
    assert [a.is_correct for a in stored1] == [True, False, False]
    correct1, _w1 = _answer_keys(test_db_session, q1["id"])
    assert correct1 == "A"
    # The FIRST short answer in served order stays position 2 with the
    # accepted EN + FR texts (existing cross-file tests depend on this).
    assert (q2["kind"], q2["position"]) == ("short_answer", 2)
    row2 = test_db_session.get(Question, q2["id"])
    assert row2.short_answer_en == "equity"
    assert row2.short_answer_fr == "capitaux propres"
    assert (q3["kind"], q3["position"]) == ("mcq", 3)
    assert "10,000" in q3["question_en"] and "10 000" in q3["question_fr"]
    correct3, _w3 = _answer_keys(test_db_session, q3["id"])
    assert correct3 == "A"


# --- 4) History preservation across re-sync (incl. double sync) --------------
def test_resync_preserves_ids_attempts_and_progress(client, test_db_session):
    """Existing Lesson 2 attempts/progress survive seed/upsert, twice over."""
    from app.learning.service import ensure_default_lessons

    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    before_ids = [q["id"] for q in qs]
    before_aids = {}
    for q in qs:
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == q["id"])
            .order_by(Answer.position)
            .all()
        )
        before_aids[q["position"]] = [a.id for a in rows]

    # Answer two questions (one right on a new question, one wrong original).
    q12 = qs[11]
    r12 = _attempt(
        client, lesson["id"], q12["id"],
        **_correct_answer_payload(test_db_session, q12),
    )
    assert r12["is_correct"] is True
    q1 = qs[0]
    _c1, w1 = _answer_keys(test_db_session, q1["id"])
    r1 = _attempt(client, lesson["id"], q1["id"], option_key=w1)
    assert r1["is_correct"] is False
    before = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert before["questions_answered"] == 2
    assert before["questions_total"] == 18
    assert before["status"] == "in_progress"

    # Re-sync twice: no concurrent/double seed may duplicate normal questions.
    ensure_default_lessons(test_db_session)
    test_db_session.commit()
    ensure_default_lessons(test_db_session)
    test_db_session.commit()
    test_db_session.expire_all()

    _lesson2, detail2 = _lesson_by_slug(client, SLUG)
    after_ids = [q["id"] for q in detail2["questions"]]
    assert after_ids == before_ids  # immutable question ids untouched
    assert [q["position"] for q in detail2["questions"]] == list(range(1, 19))
    assert len(set(after_ids)) == 18  # still no duplicates
    for q in detail2["questions"]:
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == q["id"])
            .order_by(Answer.position)
            .all()
        )
        assert [a.id for a in rows] == before_aids[q["position"]]
    # Learner history survives byte-identical through both re-syncs.
    after = detail2["progress"]
    assert after == before
    assert test_db_session.query(Attempt).count() == 2


# --- 5) Scoring on the new questions incl. short answers ---------------------
def test_scoring_new_mcq_and_short_answers(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    q4 = qs[3]  # new MCQ
    correct4, wrong4 = _answer_keys(test_db_session, q4["id"])
    bad = _attempt(client, lesson["id"], q4["id"], option_key=wrong4)
    assert bad["is_correct"] is False
    assert bad["correct_option_key"] == correct4
    good = _attempt(client, lesson["id"], q4["id"], option_key=correct4)
    assert good["is_correct"] is True
    p = good["progress"]
    assert p["questions_answered"] == 1  # one DISTINCT question, 2 rows
    assert p["questions_correct"] == 1
    assert p["questions_answered"] <= p["questions_total"] == 18


def test_new_short_answers_accept_both_languages(client, test_db_session):
    """Q6 and Q16 accept EN + FR; anything else stays wrong (straight compare)."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    by_pos = {q["position"]: q for q in detail["questions"]}
    for pos in (6, 16):
        q = by_pos[pos]
        assert q["kind"] == "short_answer"
        ok_en = _attempt(client, lesson["id"], q["id"], text="  EQUITY ")
        assert ok_en["is_correct"] is True
        assert ok_en["correct_text"] == "equity"
        ok_fr = _attempt(client, lesson["id"], q["id"], text="capitaux propres")
        assert ok_fr["is_correct"] is True
    # A wrong text on Q6 scores wrong and still offers feedback.
    q6 = by_pos[6]
    bad = _attempt(client, lesson["id"], q6["id"], text="liabilities")
    assert bad["is_correct"] is False
    assert bad["feedback"]["correction"]


# --- 6) Content completeness in BOTH languages --------------------------------
def test_content_completeness_bilingual(client):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    secs = detail["sections"]
    assert len(secs) == 10
    assert [s["position"] for s in secs] == list(range(1, 11))
    for s in secs:
        assert s["heading_en"] and s["heading_fr"]
        assert s["body_en"] and s["body_fr"]
        assert s["body_en"] != s["body_fr"]
    for q in detail["questions"]:
        assert q["question_en"] and q["question_fr"]
        assert q["question_en"] != q["question_fr"]
    bodies = "\n".join(s["body_en"] for s in secs)
    corps = "\n".join(s["body_fr"] for s in secs)
    for needle in (  # objectives, prereq, scenario, equation vocabulary
        "By the end of this lesson", "BEFORE YOU START", "Manka'a Provisions",
        "Assets = Liabilities + Equity", "RECEIVABLE", "PAYABLE",
        "capital", "Mobile Money", "Nkwen Market",
    ):
        assert needle in bodies, needle
    for needle in (
        "À la fin de cette leçon", "AVANT DE COMMENCER", "Manka'a Provisions",
        "Actif = Passif + Capitaux propres", "CRÉANCE", "DETTE",
        "capital", "Mobile Money", "Nkwen Market",
    ):
        assert needle in corps, needle
    # Worked example + guided practice figures are internally consistent.
    assert "468,000" in bodies and "468 000" in corps
    assert "218,000" in bodies and "218 000" in corps
    assert "250,000" in bodies and "250 000" in corps
    assert "478,000" in bodies and "478 000" in corps
    # Further study + honesty, EN + FR; optional academic reading is labelled
    # optional with an explicit no-endorsement statement.
    ref_en = next(s for s in secs if s["position"] == 10)["body_en"]
    ref_fr = next(s for s in secs if s["position"] == 10)["body_fr"]
    for needle in ("OHADA", "ifrs.org", "ONECCA", "OPTIONAL ACADEMIC READING",
                   "NO UBa endorsement", "does NOT make you an accountant"):
        assert needle in ref_en, needle
    for needle in ("OHADA", "ifrs.org", "ONECCA",
                   "LECTURES ACADÉMIQUES OPTIONNELLES",
                   "AUCUNE caution de l'UBa", "ne fait PAS de vous un comptable"):
        assert needle in ref_fr, needle
    # The honest-boundary final question exists in both languages (the full
    # boundary wording lives in its served options; the stem stays neutral).
    q18 = next(q for q in detail["questions"] if q["position"] == 18)
    joined_en = q18["question_en"] + " " + " ".join(
        a["text_en"] for a in q18["answers"]
    )
    joined_fr = q18["question_fr"] + " " + " ".join(
        a["text_fr"] for a in q18["answers"]
    )
    assert "accountant" in joined_en
    assert "comptable" in joined_fr


# --- 7) C1 remediation resolves inside THIS lesson, EN + FR ------------------
def test_remediation_map_resolves_to_own_sections(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    section_ids = {s["id"] for s in detail["sections"]}
    by_pos = {q["position"]: q for q in detail["questions"]}
    for pos, sec_pos in EXPECTED_REMEDIATION.items():
        q = by_pos[pos]
        if q["kind"] == "mcq":
            _correct, wrong = _answer_keys(test_db_session, q["id"])
            res = _attempt(client, lesson["id"], q["id"], option_key=wrong)
        else:
            res = _attempt(client, lesson["id"], q["id"], text="not the answer")
        assert res["is_correct"] is False, pos
        rem = res["feedback"]["remediation"]
        assert rem is not None, pos
        assert rem["lesson_id"] == lesson["id"], pos
        assert rem["section_id"] in section_ids, pos
        assert rem["section_position"] == sec_pos, pos
    # French feedback localizes the remediation label + section title.
    q5 = by_pos[5]
    _c5, w5 = _answer_keys(test_db_session, q5["id"])
    fr = _attempt(client, lesson["id"], q5["id"], lang="fr", option_key=w5)
    rem_fr = fr["feedback"]["remediation"]
    assert rem_fr["section_position"] == 5
    sec5 = next(s for s in detail["sections"] if s["position"] == 5)
    assert rem_fr["section_title"] == sec5["heading_fr"]


# --- 8) C2 review compatibility on the new questions --------------------------
def test_wrong_answer_creates_review_without_duplicating_sequence(
    client, test_db_session
):
    """A miss on a NEW Lesson 2 question creates exactly one card; the served
    normal sequence is unchanged and the next question is a DISTINCT one."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    q = qs[4]  # position 5, new MCQ
    _correct, wrong = _answer_keys(test_db_session, q["id"])
    res = _attempt(client, lesson["id"], q["id"], option_key=wrong)
    assert res["is_correct"] is False
    assert res["question_id"] == q["id"]
    assert res["feedback"]["remediation"] is not None  # C1 still offered

    cards = _reviews(client)
    assert len(cards) == 1
    assert cards[0]["question_id"] == q["id"]
    assert cards[0]["lesson_id"] == lesson["id"]
    assert cards[0]["is_due"] is True

    # The normal sequence, served again, is the SAME fixed list — no question
    # was re-inserted, duplicated, or reordered by the wrong answer.
    _lesson2, detail2 = _lesson_by_slug(client, SLUG)
    assert [x["id"] for x in detail2["questions"]] == [x["id"] for x in qs]
    nxt = detail2["questions"][5]
    assert nxt["id"] != q["id"]  # the next question is a DISTINCT question
    assert nxt["position"] == q["position"] + 1  # counter moves on exactly +1


def test_review_correction_updates_mastery_for_same_question_id(
    client, test_db_session
):
    """Session 18 contract on Lesson 2: a correct review answer records one
    attempt on the SAME immutable question id and rolls mastery up."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    by_pos = {q["position"]: q for q in qs}
    for q in qs:  # answer everything correctly except position 5
        if q["position"] == 5:
            continue
        _attempt(
            client, lesson["id"], q["id"],
            **_correct_answer_payload(test_db_session, q),
        )
    q5 = by_pos[5]
    _c5, w5 = _answer_keys(test_db_session, q5["id"])
    _attempt(client, lesson["id"], q5["id"], option_key=w5)

    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_total"] == 18
    assert progress["questions_answered"] == 18  # 18/18
    assert progress["questions_correct"] == 17  # one initial error
    assert progress["best_score"] == 94  # round(17 / 18 * 100)
    assert progress["status"] == "completed"  # every question visited

    card = _reviews(client)[0]
    assert card["question_id"] == q5["id"]
    attempts_before = {a.id for a in test_db_session.query(Attempt).all()}
    res = _answer_review(client, card["id"], option_key=_c5)
    assert res["correct"] is True
    after = test_db_session.query(Attempt).all()
    new_rows = [a for a in after if a.id not in attempts_before]
    assert len(new_rows) == 1  # exactly one append-only resolution row
    assert new_rows[0].question_id == q5["id"]  # on the SAME immutable id
    assert new_rows[0].is_correct is True

    # The authoritative roll-up now reflects the corrected resolution.
    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_total"] == 18
    assert progress["questions_answered"] == 18
    assert progress["questions_correct"] == 18
    assert progress["best_score"] == 100

    # The review payload never carries the answer key.
    raw = json.dumps(res)
    for forbidden in ("correct_option_key", "correct_text", "is_correct"):
        assert forbidden not in raw, forbidden


# --- 9) Progress invariants on a full walk ------------------------------------
def test_full_walk_counts_distinct_ids_and_never_exceeds_total(
    client, test_db_session
):
    """Answering all 18 (with retries) completes at 100; counts stay bounded."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    # Wrong-then-right on position 4 first: retries must not inflate counts.
    q4 = qs[3]
    c4, w4 = _answer_keys(test_db_session, q4["id"])
    _attempt(client, lesson["id"], q4["id"], option_key=w4)
    _attempt(client, lesson["id"], q4["id"], option_key=c4)
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert p["questions_answered"] == 1  # position 4 only so far
    assert p["questions_correct"] == 1
    assert p["status"] == "in_progress"
    # Now walk the WHOLE fixed sequence, answering every position correctly
    # (position 4 is re-answered on purpose — a retry, not a new question).
    _lesson, detail = _lesson_by_slug(client, SLUG)  # refresh served rows
    for q in detail["questions"]:
        _attempt(
            client, lesson["id"], q["id"],
            **_correct_answer_payload(test_db_session, q),
        )
    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_total"] == 18
    assert progress["questions_answered"] == 18
    assert progress["questions_correct"] == 18
    assert progress["status"] == "completed"
    assert progress["best_score"] == 100
    assert progress["questions_answered"] <= progress["questions_total"]
    assert progress["questions_correct"] <= progress["questions_total"]


# --- 10) Certificate behavior with the expanded lesson -----------------------
def test_expanded_lesson_feeds_completion_but_course_still_locked(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    for q in detail["questions"]:
        _attempt(
            client, lesson["id"], q["id"],
            **_correct_answer_payload(test_db_session, q),
        )
    completion = client.get("/learning/completion").json()
    assert completion["total_lessons"] == 7
    assert completion["completed_lessons"] == 1
    assert completion["completed"] is False
    assert completion["certificate_status"] == "locked"
    assert client.post("/learning/certificate").status_code == 403


# --- 11) Lesson 1 regression guard -------------------------------------------
def test_lesson1_18_question_sequence_review_and_certificate_unchanged(
    client, test_db_session
):
    """Lesson 1 keeps its fixed 18-question identity, progress,
    review-to-mastery and certificate rule after the Lesson 2 expansion sync."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    qs = detail["questions"]
    assert len(qs) == 18
    assert len({q["id"] for q in qs}) == 18
    assert [q["position"] for q in qs] == list(range(1, 19))
    assert detail["progress"]["questions_total"] == 18

    for q in qs:  # all right except position 3
        if q["position"] == 3:
            _c, w = _answer_keys(test_db_session, q["id"])
            _attempt(client, lesson["id"], q["id"], option_key=w)
        else:
            _attempt(
                client, lesson["id"], q["id"],
                **_correct_answer_payload(test_db_session, q),
            )
    progress = _lesson_by_slug(client, "what-is-accounting")[1]["progress"]
    assert progress["questions_total"] == 18
    assert progress["questions_answered"] == 18
    assert progress["questions_correct"] == 17
    assert progress["best_score"] == 94
    assert progress["status"] == "completed"

    card = _reviews(client)[0]
    missed = next(q for q in qs if q["id"] == card["question_id"])
    assert missed["position"] == 3
    correct, _w = _answer_keys(test_db_session, missed["id"])
    res = _answer_review(client, card["id"], option_key=correct)
    assert res["correct"] is True
    progress = _lesson_by_slug(client, "what-is-accounting")[1]["progress"]
    assert progress["questions_correct"] == 18
    assert progress["best_score"] == 100
    # status == "completed" AND best_score == 100 for one lesson alone never
    # unlocks the course certificate.
    assert client.post("/learning/certificate").status_code == 403


# --- 12) Answer-key protection ------------------------------------------------
def test_read_endpoints_never_expose_the_answer_key(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    raw = json.dumps(detail)
    assert "is_correct" not in raw
    assert "explanation" not in raw
    for option in detail["questions"][0]["answers"]:
        assert set(option.keys()) == {"option_key", "text_en", "text_fr"}
    section = detail["sections"][0]
    assert isinstance(section["id"], int)
    assert set(section.keys()) == {
        "id",
        "position",
        "heading_en",
        "heading_fr",
        "body_en",
        "body_fr",
    }


