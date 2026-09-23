"""Lesson 1 expansion tests (Session 15).

The original 2-question/3-section Lesson 1 was upgraded IN PLACE into a full
beginner lesson (10 sections + 10 questions, built around the "Manka'a
Provisions" scenario) WITHOUT touching the engine: same slug
("what-is-accounting"), same curriculum position, and the two ORIGINAL
questions keep their positions (1, 2), question ids, answer ids, option keys
and correct answers (A correct on both), so historical attempts, progress
rows, review cards, certificate eligibility and the Lesson 4 practice
connector are all preserved.

These tests pin, for the expanded content:
1. Identity: slug/position and the 7-lesson curriculum order are unchanged.
2. Content completeness: every requested beginner element is present in BOTH
   languages (objectives, prerequisite note, scenario, purpose, bookkeeping
   vs accounting, users, events + source documents, vocabulary, worked
   example, guided practice, further study, honest disclaimers).
3. History preservation: question/answer ids are stable across re-sync and
   attempts/progress rows survive it; new questions grow questions_total.
4. Scoring: correct/incorrect grading on the new questions including the
   short answer (accepted EN + FR, language-blind); best_score roll-up.
5. Answer-key protection: read endpoints never leak key material.
6. EN/FR behavior: feedback language selection + localized remediation.
7. Remediation (C1): every question's target resolves to the intended
   section of the SAME lesson (deterministic position map).
8. Review compatibility (C2): new questions create cards on wrong/guessed
   answers, climb the ladder, and never touch attempts or the key.
9. Lesson 4 connector assumptions unchanged; Lesson 1 adds NO practice post.
10. Certificate behavior: the expanded lesson feeds course completion; the
    course stays locked on Lesson 1 alone.
"""
import json

from app.models.learning import Answer, Attempt
from app.tests.test_learning import (
    EXPECTED_SLUGS,
    _answer_keys,
    _attempt,
    _lesson_by_slug,
    _register,
)

SLUG = "what-is-accounting"

# position of question -> position of the section its remediation points at
# (authored in the seed; must always resolve to a real section of THIS lesson).
EXPECTED_REMEDIATION = {
    1: 3,   # purpose of accounting      -> "Why it matters"
    2: 7,   # transaction definition     -> "Five words..."
    3: 4,   # bookkeeping vs accounting  -> same-named section
    4: 6,   # source documents           -> "Where records come from..."
    5: 7,   # asset vs expense           -> "Five words..."
    6: 5,   # users of the numbers       -> "Who reads the numbers?"
    7: 7,   # "owes" short answer        -> "Five words..."
    8: 8,   # credit-sale application    -> worked example
    9: 9,   # cash difference            -> guided practice
    10: 10, # honest boundary            -> references + honest note
}


def _bodies(detail, lang):
    """section position -> heading + body, one language."""
    return {
        s["position"]: f"{s[f'heading_{lang}'] or ''}\n{s[f'body_{lang}']}"
        for s in detail["sections"]
    }


# --- 1) Identity --------------------------------------------------------------
def test_lesson1_identity_and_curriculum_unchanged(client):
    _register(client)
    lessons = client.get("/learning/lessons").json()
    assert [l["slug"] for l in lessons] == EXPECTED_SLUGS
    first = lessons[0]
    assert first["slug"] == SLUG
    assert first["position"] == 1
    assert first["progress"]["questions_total"] == 10


# --- 2) Structure ---------------------------------------------------------------
def test_lesson1_full_beginner_structure(client):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    secs, qs = detail["sections"], detail["questions"]
    assert len(secs) == 10 and len(qs) == 10
    assert [s["position"] for s in secs] == list(range(1, 11))
    assert [q["position"] for q in qs] == list(range(1, 11))
    for s in secs:
        assert s["heading_en"] and s["heading_fr"]
        assert s["body_en"] and s["body_fr"]
        assert s["body_en"] != s["body_fr"]
    kinds = {q["position"]: q["kind"] for q in qs}
    assert kinds == {
        1: "mcq", 2: "mcq", 3: "mcq", 4: "mcq", 5: "mcq", 6: "mcq",
        7: "short_answer", 8: "mcq", 9: "mcq", 10: "mcq",
    }
    # original questions keep exactly 3 options with A correct (pinned by the
    # Session 11 tests; kept stable here on purpose).
    for pos in (1, 2):
        q = qs[pos - 1]
        assert len(q["answers"]) == 3
        assert [a["option_key"] for a in q["answers"]] == ["A", "B", "C"]


# --- 3) Content completeness (bilingual) --------------------------------------
def test_lesson1_required_content_elements_bilingual(client):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    en, fr = _bodies(detail, "en"), _bodies(detail, "fr")
    all_en, all_fr = "\n".join(en.values()), "\n".join(fr.values())

    # Scenario (a real local business used consistently, EN + FR).
    assert "Manka'a Provisions" in all_en
    assert "Manka'a Provisions" in all_fr
    # Learning objectives + prerequisite note (Section 1).
    assert "By the end of this lesson you will be able to" in en[1]
    assert "BEFORE YOU START" in en[1]
    assert "vous serez capable" in fr[1]
    assert "AVANT DE COMMENCER" in fr[1]
    # Accounting purpose ("Why it matters").
    assert detail["sections"][2]["heading_en"] == "Why it matters"
    assert "pay the right taxes" in en[3]
    # Bookkeeping versus accounting (its own section).
    assert "Bookkeeping is the daily recording" in en[4]
    assert "La tenue de livres est l'enregistrement quotidien" in fr[4]
    # Users of accounting information.
    assert "bank" in en[5] and "tax authority" in en[5] and "suppliers" in en[5]
    # Business events + source documents.
    assert "source document" in en[6] and "Mobile Money" in en[6]
    assert "pièce justificative" in fr[6]
    # Beginner vocabulary: the five words, both languages.
    for word in ("TRANSACTION", "ASSET", "LIABILITY", "INCOME", "EXPENSE"):
        assert word in en[7]
    for word in ("TRANSACTION", "ACTIF", "PASSIF", "PRODUIT", "CHARGE"):
        assert word in fr[7]
    # Worked example (deterministic numbers from the scenario day).
    assert "44,000 FCFA" in en[8] and "102,000" in en[8]
    assert "150 000 FCFA" in fr[8]
    # Guided practice.
    assert "check yourself" in en[9]
    # Further study: authoritative sources.
    assert "AUTHORITATIVE SOURCES" in en[10]
    for token in ("ohada.org", "ifrs.org", "ifac.org", "accaglobal.com"):
        assert token in en[10]
    # Clearly-labelled optional academic references.
    assert "OPTIONAL ACADEMIC READING" in en[10]
    assert "Neba, Akoso Wilfred" in en[10]
    assert "Kueda Wamba, Berthelo" in en[10]
    assert "Google Scholar or AJOL" in en[10]
    # Honesty: no professional-status claim, no endorsement claim.
    assert "does NOT make you an accountant" in en[10]
    assert "ne fait PAS de vous un comptable" in fr[10]
    assert "ONECCA" in en[10] and "ONECCA" in fr[10]
    assert "NO UBa endorsement" in en[10]
    assert "AUCUNE caution de l'UBa" in fr[10]
    assert "nothing from them is copied into this platform" in en[10]
    assert "rien de leur contenu n'est copié" in fr[10]


# --- 4) History preservation across re-sync -----------------------------------
def test_original_questions_and_answer_ids_preserved_across_resync(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    assert qs[0]["question_en"] == "What is the main purpose of accounting for a business?"
    assert qs[1]["question_en"] == "A 'transaction' in accounting is…"

    before_qids = {q["position"]: q["id"] for q in qs}
    before_aids = {}
    for q in qs:
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == q["id"])
            .order_by(Answer.position)
            .all()
        )
        before_aids[q["position"]] = [a.id for a in rows]

    from app.learning.service import ensure_default_lessons

    ensure_default_lessons(test_db_session)
    test_db_session.commit()

    after = _lesson_by_slug(client, SLUG)[1]
    after_qids = {q["position"]: q["id"] for q in after["questions"]}
    assert before_qids == after_qids, "question ids changed during resync"
    for pos, ids in before_aids.items():
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == before_qids[pos])
            .order_by(Answer.position)
            .all()
        )
        assert [a.id for a in rows] == ids, f"answer ids changed at position {pos}"
    # The two ORIGINAL questions keep their exact option keys + correct flags.
    for pos in (1, 2):
        rows = (
            test_db_session.query(Answer)
            .filter(Answer.question_id == before_qids[pos])
            .order_by(Answer.position)
            .all()
        )
        assert [a.option_key for a in rows] == ["A", "B", "C"]
        assert [a.is_correct for a in rows] == [True, False, False]
    assert len(after["questions"]) == 10


def test_attempt_and_progress_survive_resync(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    q1 = detail["questions"][0]
    _correct, wrong = _answer_keys(test_db_session, q1["id"])
    _attempt(client, lesson["id"], q1["id"], option_key=wrong)
    attempt_id = (
        test_db_session.query(Attempt).order_by(Attempt.id.desc()).first().id
    )
    before = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert before["questions_answered"] == 1 and before["questions_correct"] == 0

    from app.learning.service import ensure_default_lessons

    ensure_default_lessons(test_db_session)
    test_db_session.commit()

    assert (
        test_db_session.query(Attempt).filter(Attempt.id == attempt_id).first()
        is not None
    )
    after = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert after["questions_answered"] == 1
    assert after["questions_correct"] == 0
    assert after["questions_total"] == 10
    assert after["best_score"] == 0
    assert after["status"] == "in_progress"


# --- 5) Scoring (formative + final, incl. the short answer) --------------------
def test_scoring_covers_formative_and_final_questions(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    by_pos = {q["position"]: q for q in detail["questions"]}

    # Grade EVERY question correctly (the certificate test does the same).
    for q in detail["questions"]:
        if q["kind"] == "mcq":
            correct, _wrong = _answer_keys(test_db_session, q["id"])
            r = _attempt(client, lesson["id"], q["id"], option_key=correct)
        else:
            r = _attempt(client, lesson["id"], q["id"], text="liability")
        assert r["is_correct"] is True, q["position"]

    progress = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert progress["questions_answered"] == 10
    assert progress["questions_correct"] == 10
    assert progress["best_score"] == 100
    assert progress["status"] == "completed"

    # The short answer accepts BOTH stored languages (language-blind scoring).
    assert _attempt(client, lesson["id"], by_pos[7]["id"], text="passif")[
        "is_correct"
    ] is True
    assert _attempt(client, lesson["id"], by_pos[7]["id"], text="  LIABILITY ")["is_correct"] is True  # normalised
    assert _attempt(client, lesson["id"], by_pos[7]["id"], text="not-a-word")[
        "is_correct"
    ] is False

    # Roll-up over ALL attempts: 14 answered, 13 correct -> 93.
    correct1, _w = _answer_keys(test_db_session, by_pos[1]["id"])
    _attempt(client, lesson["id"], by_pos[1]["id"], option_key=correct1)
    final = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert final["questions_answered"] == 14
    assert final["questions_correct"] == 13
    assert final["best_score"] == 93  # round(13 / 14 * 100)
    assert final["status"] == "completed"


# --- 6) EN/FR feedback + learner-safety on a NEW question ----------------------
def test_feedback_language_and_no_key_leak_on_new_question(client, test_db_session):
    _register(client)  # stored preference: 'en'
    lesson, detail = _lesson_by_slug(client, SLUG)
    q3 = detail["questions"][2]  # bookkeeping vs accounting (new, formative)
    correct, wrong = _answer_keys(test_db_session, q3["id"])

    as_en = _attempt(client, lesson["id"], q3["id"], lang="en", option_key=wrong)
    as_fr = _attempt(client, lesson["id"], q3["id"], lang="fr", option_key=wrong)
    assert as_en["is_correct"] is False and as_fr["is_correct"] is False
    assert as_en["feedback"]["explanation"] != as_fr["feedback"]["explanation"]
    assert as_en["feedback"]["correction"] != as_fr["feedback"]["correction"]
    assert as_en["feedback"]["remediation"]["action_label"] == "Review this concept"
    assert as_fr["feedback"]["remediation"]["action_label"] == "Revoir ce concept"

    # Stored preference drives the default language (no lang param).
    no_lang = _attempt(client, lesson["id"], q3["id"], option_key=wrong)
    assert no_lang["feedback"]["explanation"] == as_en["feedback"]["explanation"]

    # Learner-safe: the CORRECT option's text is never echoed in the feedback.
    correct_answer = next(a for a in q3["answers"] if a["option_key"] == correct)
    raw = str(as_en["feedback"]) + str(as_fr["feedback"])
    assert correct_answer["text_en"] not in raw
    assert correct_answer["text_fr"] not in raw
    assert "is_correct" not in raw


# --- 7) Remediation targets (C1) — deterministic position map ------------------
def test_every_question_remediation_targets_its_own_section(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    section_ids = {s["position"]: s["id"] for s in detail["sections"]}

    for q in detail["questions"]:
        if q["kind"] == "mcq":
            _correct, wrong = _answer_keys(test_db_session, q["id"])
            r = _attempt(client, lesson["id"], q["id"], option_key=wrong)
        else:
            r = _attempt(client, lesson["id"], q["id"], text="nope")
        rem = r["feedback"]["remediation"]
        expected = EXPECTED_REMEDIATION[q["position"]]
        assert rem["lesson_id"] == lesson["id"]
        assert rem["section_position"] == expected
        assert rem["section_id"] == section_ids[expected]

    # Correct answers carry NO remediation target.
    q1 = detail["questions"][0]
    correct, _w = _answer_keys(test_db_session, q1["id"])
    r = _attempt(client, lesson["id"], q1["id"], option_key=correct)
    assert r["feedback"]["remediation"] is None


# --- 8) Answer-key protection across reads -------------------------------------
def test_lesson1_reads_never_expose_the_key(client):
    _register(client)
    listing = client.get("/learning/lessons")
    for forbidden in ("explanation", "correction", "remediation", "is_correct"):
        assert forbidden not in listing.text, forbidden

    _lesson, detail = _lesson_by_slug(client, SLUG)
    raw = json.dumps(detail)
    for forbidden in (
        "explanation_en", "explanation_fr", "correction_en", "correction_fr",
        "remediation", "is_correct", "correct_option_key", "correct_text",
        "short_answer_en", "short_answer_fr", "practice_amount",
    ):
        assert forbidden not in raw, forbidden
    for q in detail["questions"]:
        assert set(q.keys()) == {
            "id", "position", "question_en", "question_fr", "kind",
            "answers", "posts_demo_transaction",
        }
        for a in q["answers"]:
            assert set(a.keys()) == {"option_key", "text_en", "text_fr"}


# --- 9) Review compatibility (C2) on NEW questions ------------------------------
def test_new_final_question_review_card_compatibility(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    q8 = detail["questions"][7]  # credit-sale application (new, final)
    correct, wrong = _answer_keys(test_db_session, q8["id"])
    _attempt(client, lesson["id"], q8["id"], option_key=wrong)

    cards = client.get("/learning/reviews").json()
    assert len(cards) == 1
    card = cards[0]
    assert card["question_id"] == q8["id"]
    assert card["lesson_id"] == lesson["id"]
    assert card["lesson_title_en"] == "What Accounting Is and Why It Matters"
    assert card["is_due"] is True

    raw = client.get("/learning/reviews").text
    for forbidden in ("correct_option_key", "correct_text", "is_correct"):
        assert forbidden not in raw, forbidden

    # Answer the card correctly: ladder step 1 = +1 day.
    r = client.post(f"/learning/reviews/{card['id']}/answer", json={"option_key": correct})
    body = r.json()
    assert body["correct"] is True
    assert body["stage"] == 1
    assert body["interval_days"] == 1

    # Review answers create NO attempt rows.
    attempts_before = test_db_session.query(Attempt).count()
    client.post(f"/learning/reviews/{card['id']}/answer", json={"option_key": correct})
    assert test_db_session.query(Attempt).count() == attempts_before


def test_confidence_rules_apply_to_new_questions(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    q6 = detail["questions"][5]
    correct, _w = _answer_keys(test_db_session, q6["id"])

    # Confident correct answer: no review card.
    _attempt(client, lesson["id"], q6["id"], option_key=correct, confidence="understood")
    assert client.get("/learning/reviews/summary").json()["total_active"] == 0

    # Guessed correct answer: a card IS created (deterministic C2 rule).
    _attempt(client, lesson["id"], q6["id"], option_key=correct, confidence="guessed")
    summary = client.get("/learning/reviews/summary").json()
    assert summary["total_active"] == 1
    assert summary["due_now"] == 1


# --- 10) Lesson 4 connector assumptions unchanged -------------------------------
def test_lesson4_connector_assumptions_unchanged(client):
    _register(client)
    lessons = client.get("/learning/lessons").json()
    lesson4 = next(l for l in lessons if l["slug"] == "journal-entries")
    assert lesson4["position"] == 4
    d1 = _lesson_by_slug(client, SLUG)[1]
    d4 = client.get(f"/learning/lessons/{lesson4['id']}").json()
    # Lesson 1 adds NO practice-posting question; Lesson 4 keeps exactly one.
    assert not any(q["posts_demo_transaction"] for q in d1["questions"])
    practice = [q for q in d4["questions"] if q["posts_demo_transaction"]]
    assert len(practice) == 1 and practice[0]["position"] == 1


# --- 11) Certificate/completion behavior with the expanded lesson ----------------
def test_expanded_lesson_feeds_completion_but_course_still_locked(
    client, test_db_session
):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    for q in detail["questions"]:
        if q["kind"] == "mcq":
            correct, _w = _answer_keys(test_db_session, q["id"])
            _attempt(client, lesson["id"], q["id"], option_key=correct)
        else:
            _attempt(client, lesson["id"], q["id"], text="liability")

    completion = client.get("/learning/completion").json()
    assert completion["total_lessons"] == 7
    assert completion["completed_lessons"] == 1
    assert completion["completed"] is False
    assert completion["certificate_status"] == "locked"
    assert client.post("/learning/certificate").status_code == 403
