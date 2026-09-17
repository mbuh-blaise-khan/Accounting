"""Learning engine tests (Session 11 Part A + Part C1).

Covers the acceptance points:
1. The 7 lessons seed in the exact ACCA-FIA curriculum order, EN+FR.
2. Lesson detail serves sections + questions per-request; correct answers are
   NOT exposed by the read endpoints (content-protection requirement).
3. Scoring: correct/incorrect MCQ + short-answer straight comparison.
4. Per-user progress roll-up (two users are fully independent).
5. Language toggle respected: every payload carries both en/fr variants.
6. Lesson 4 practice connector posts a REAL balanced transaction into the
   demo workspace end-to-end (and does NOT post on a wrong answer).
7. Part C1 — post-answer feedback: explanations/corrections returned ONLY by
   the submission endpoint, in the requested language, never carrying the
   answer key, with an optional remediation target scoped to the question's
   own lesson.
"""
import json
from decimal import Decimal
from types import SimpleNamespace

from app.learning import feedback as feedback_copy
from app.learning.service import _remediation_target
from app.models.learning import Answer, Attempt, Lesson, LessonSection, Question
from app.models.user import User
from app.models.user import User


def _signed_in_user(db, email: str = "learner@example.com"):
    """Get the User object for the currently signed-in test user by email."""
    return db.query(User).filter(User.email == email).first()


def _signed_in_user(db, email: str = "learner@example.com"):
    """Get the User object for the currently signed-in test user by email."""
    return db.query(User).filter(User.email == email).first()


def _answer_keys(db, question_id):
    """(correct_option_key, wrong_option_key) straight from the stored answers.

    Reading the key from the database is what lets a test drive BOTH the correct
    and the incorrect grading path deterministically — the API never reveals
    which option is correct before an answer is submitted.
    """
    rows = db.query(Answer).filter(Answer.question_id == question_id).all()
    correct = next(a.option_key for a in rows if a.is_correct)
    wrong = next(a.option_key for a in rows if not a.is_correct)
    return correct, wrong


def _register(client, email="learner@example.com", name="Learner", lang="en"):
    # register-no-auto-login: register no longer sets the auth cookie, so the
    # test session is established by an explicit login right after.
    r = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "display_name": name,
            "language_preference": lang,
        },
    )
    assert r.status_code == 200, r.text
    login = client.post(
        "/auth/login", json={"email": email, "password": "supersecret123"}
    )
    assert login.status_code == 200, login.text
    return r.json()


def _create_org(client, framework="OHADA", name="Learn Co"):
    r = client.post(
        "/organizations",
        json={"name": name, "framework": framework, "currency": "XAF", "is_demo": True},
    )
    assert r.status_code == 201, r.text
    return r.json()


def _lessons(client):
    r = client.get("/learning/lessons")
    assert r.status_code == 200, r.text
    return r.json()


def _lesson(client, lesson_id):
    r = client.get(f"/learning/lessons/{lesson_id}")
    assert r.status_code == 200, r.text
    return r.json()


def _attempt(client, lesson_id, question_id, lang=None, **extra):
    """Submit one answer. `lang` selects the requested feedback language."""
    payload = {"lesson_id": lesson_id, "question_id": question_id, **extra}
    url = f"/learning/attempts?lang={lang}" if lang else "/learning/attempts"
    r = client.post(url, json=payload)
    assert r.status_code == 200, r.text
    return r.json()


EXPECTED_SLUGS = [
    "what-is-accounting",
    "the-accounting-equation",
    "debits-and-credits",
    "journal-entries",
    "journal-to-ledger",
    "the-trial-balance",
    "reading-financial-statements",
]
# --- 1) Seed + curriculum order + language variant presence ------------------
def test_learning_seeds_seven_lessons_in_curriculum_order(client):
    _register(client)
    lessons = _lessons(client)
    assert [l["slug"] for l in lessons] == EXPECTED_SLUGS
    assert [l["position"] for l in lessons] == [1, 2, 3, 4, 5, 6, 7]
    for lesson in lessons:
        assert lesson["title_en"] and lesson["title_fr"]
        assert lesson["title_en"] != lesson["title_fr"]  # both languages real
        assert lesson["summary_en"] and lesson["summary_fr"]
        assert lesson["progress"]["status"] == "not_started"
        assert lesson["progress"]["questions_total"] >= 2
        # Answers are never exposed at the list level either.
        assert "answers" not in lesson


def test_learning_needs_authentication(client):
    assert client.get("/learning/lessons").status_code == 401
    assert client.get("/learning/lessons/1").status_code == 401
    assert client.post("/learning/attempts", json={}).status_code == 401


# --- 2) Lesson detail: content served per-request, answers hidden ------------
def test_lesson_detail_serves_content_but_never_reveals_correct_answers(client):
    _register(client)
    lessons = _lessons(client)
    lesson4 = next(l for l in lessons if l["slug"] == "journal-entries")
    detail = _lesson(client, lesson4["id"])

    assert len(detail["sections"]) >= 2
    assert all(sec["body_en"] and sec["body_fr"] for sec in detail["sections"])
    assert len(detail["questions"]) >= 2
    for q in detail["questions"]:
        assert q["question_en"] and q["question_fr"]
        # Content-protection: the read endpoint NEVER leaks is_correct.
        assert "is_correct" not in q
        for a in q["answers"]:
            assert a["option_key"]
            assert a["text_en"] and a["text_fr"]
            assert "is_correct" not in a
    # The practice question is clearly flagged for the UI.
    assert any(q["posts_demo_transaction"] for q in detail["questions"])


def test_unknown_lesson_returns_404(client):
    _register(client)
    assert client.get("/learning/lessons/99999").status_code == 404
# --- 3) Scoring: MCQ + short answer, straight comparison ---------------------
def test_mcq_scoring_correct_and_incorrect(client):
    _register(client)
    lessons = _lessons(client)
    lesson1 = next(l for l in lessons if l["slug"] == "what-is-accounting")
    detail = _lesson(client, lesson1["id"])
    q1 = detail["questions"][0]
    assert q1["kind"] == "mcq"
    assert len(q1["answers"]) == 3  # 'A' is the stored correct option

    wrong = _attempt(client, lesson1["id"], q1["id"], option_key="B")
    assert wrong["is_correct"] is False
    assert wrong["correct_option_key"] == "A"  # revealed only after grading
    assert wrong["explanation_en"]

    right = _attempt(client, lesson1["id"], q1["id"], option_key="A")
    assert right["is_correct"] is True
    assert right["correct_option_key"] == "A"
    assert right["progress"]["questions_answered"] == 2
    assert right["progress"]["questions_correct"] == 1


def test_short_answer_accepts_both_languages_straight_comparison(client):
    _register(client)
    lessons = _lessons(client)
    lesson2 = next(l for l in lessons if l["slug"] == "the-accounting-equation")
    detail = _lesson(client, lesson2["id"])
    sa = next(q for q in detail["questions"] if q["kind"] == "short_answer")

    # English accepted.
    ok_en = _attempt(client, lesson2["id"], sa["id"], text="  EQUITY ")
    assert ok_en["is_correct"] is True
    assert ok_en["correct_text"] == "equity"
    # French accepted too (language toggle respected at the scoring layer).
    ok_fr = _attempt(client, lesson2["id"], sa["id"], text="capitaux propres")
    assert ok_fr["is_correct"] is True
    # Wrong answer straight-comparison-fails.
    bad = _attempt(client, lesson2["id"], sa["id"], text="liabilities")
    assert bad["is_correct"] is False


def test_mcq_requires_option_key(client):
    _register(client)
    lessons = _lessons(client)
    lesson1 = next(l for l in lessons if l["slug"] == "what-is-accounting")
    detail = _lesson(client, lesson1["id"])
    r = client.post(
        "/learning/attempts",
        json={"lesson_id": lesson1["id"], "question_id": detail["questions"][0]["id"]},
    )
    assert r.status_code == 422
# --- 4) Per-user progress isolation ------------------------------------------
def test_progress_is_recorded_per_user(client):
    # Alice registers, learns, and her progress is recorded for HER.
    _register(client, email="alice@example.com", name="Alice")
    lessons = _lessons(client)
    lesson6 = next(l for l in lessons if l["slug"] == "the-trial-balance")
    detail = _lesson(client, lesson6["id"])
    q = detail["questions"][0]
    res = _attempt(client, lesson6["id"], q["id"], option_key="A")
    assert res["is_correct"] is True

    alice_after = next(
        l for l in _lessons(client) if l["id"] == lesson6["id"]
    )["progress"]
    assert alice_after["questions_answered"] == 1
    assert alice_after["status"] == "in_progress"

    # Only NOW does Bob register (taking over the client's session cookie);
    # his progress for the same lesson is completely untouched.
    _register(client, email="bob@example.com", name="Bob")
    bob_lessons = _lessons(client)
    bob_progress = next(l for l in bob_lessons if l["id"] == lesson6["id"])[
        "progress"
    ]
    assert bob_progress["questions_answered"] == 0
    assert bob_progress["status"] == "not_started"


# --- 5) Lesson 4 practice connector: real posting end-to-end -----------------
def test_lesson4_correct_answer_posts_real_ohada_transaction(client):
    _register(client)
    org = _create_org(client, framework="OHADA")
    lessons = _lessons(client)
    lesson4 = next(l for l in lessons if l["slug"] == "journal-entries")
    detail = _lesson(client, lesson4["id"])
    practice = next(q for q in detail["questions"] if q["posts_demo_transaction"])

    res = _attempt(
        client,
        lesson4["id"],
        practice["id"],
        option_key="A",  # the correct cash-sale entry
        organization_id=org["id"],
    )
    assert res["is_correct"] is True
    assert res["practice_posted"] is True
    assert res["practice_transaction_id"] is not None
    assert res["practice_error"] is None

    # The transaction is REALLY there, posted + balanced, at org level.
    txns = client.get(f"/transactions?organization_id={org['id']}").json()
    posted = [t for t in txns if t["id"] == res["practice_transaction_id"]]
    assert len(posted) == 1
    assert posted[0]["status"] == "posted"
    lines = posted[0]["lines"]
    assert len(lines) == 2
    codes = {line["account_code"] for line in lines}
    assert codes == {"5711", "7011"}  # OHADA Cash / Sales-of-goods
    by_code = {line["account_code"]: line for line in lines}
    assert Decimal(by_code["5711"]["debit_amount"]) == Decimal("25000")
    assert Decimal(by_code["7011"]["credit_amount"]) == Decimal("25000")

    # It shows up in the trial balance (full accounting cycle visible).
    tb = client.get(f"/trial-balance?organization_id={org['id']}").json()
    assert tb["balanced"] is True
    assert float(tb["totals"]["closing_debit"]) == 25000.0


def test_lesson4_wrong_answer_does_not_post(client):
    _register(client)
    org = _create_org(client, framework="OHADA")
    lessons = _lessons(client)
    lesson4 = next(l for l in lessons if l["slug"] == "journal-entries")
    detail = _lesson(client, lesson4["id"])
    practice = next(q for q in detail["questions"] if q["posts_demo_transaction"])

    res = _attempt(
        client,
        lesson4["id"],
        practice["id"],
        option_key="B",  # wrong entry
        organization_id=org["id"],
    )
    assert res["is_correct"] is False
    assert res["practice_posted"] is False
    assert res["practice_transaction_id"] is None
    assert client.get(f"/transactions?organization_id={org['id']}").json() == []


def test_lesson4_practice_posting_works_for_ifrs_names_too(client):
    _register(client)
    org = _create_org(client, framework="IFRS")
    lessons = _lessons(client)
    lesson4 = next(l for l in lessons if l["slug"] == "journal-entries")
    detail = _lesson(client, lesson4["id"])
    practice = next(q for q in detail["questions"] if q["posts_demo_transaction"])

    res = _attempt(
        client,
        lesson4["id"],
        practice["id"],
        option_key="A",
        organization_id=org["id"],
    )
    assert res["is_correct"] is True
    assert res["practice_posted"] is True, res
    posted = client.get(f"/transactions?organization_id={org['id']}").json()
    match = [t for t in posted if t["id"] == res["practice_transaction_id"]]
    assert len(match) == 1
    names = {line["account_name_en"] for line in match[0]["lines"]}
    assert "Cash and cash equivalents" in names
    assert "Sales revenue" in names


def _lesson_by_slug(client, slug):
    """(lesson summary, lesson detail) for a slug — straight from the API."""
    lesson = next(l for l in _lessons(client) if l["slug"] == slug)
    return lesson, _lesson(client, lesson["id"])


def _stored_question(session, question_id):
    """The question row as stored server-side (what the API only reveals after
    a submission). `expire_all` first so the read is not stale after API calls
    that ran in the app's own session."""
    session.expire_all()
    return session.get(Question, question_id)


# --- 7) Part C1 — answer protection before submission ------------------------
def test_lesson_reads_never_expose_feedback_material(client, test_db_session):
    """Nothing about the answer key, the explanation or remediation may be
    reachable before an answer is submitted (Part C1 protection requirement)."""
    _register(client)

    # Lesson LIST: no section, question or feedback material at all.
    listing = client.get("/learning/lessons")
    assert listing.status_code == 200
    for forbidden in ("explanation", "correction", "remediation", "is_correct"):
        assert forbidden not in listing.text, forbidden

    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    raw = json.dumps(detail)
    for forbidden in (
        "explanation_en",
        "explanation_fr",
        "correction_en",
        "correction_fr",
        "remediation",
        "is_correct",
        "correct_option_key",
        "correct_text",
        "short_answer_en",
        "short_answer_fr",
        "practice_amount",
    ):
        assert forbidden not in raw, forbidden

    # The question payload is exactly the pre-submission shape (no extra fields
    # could smuggle feedback in), and so is each option.
    q = detail["questions"][0]
    assert set(q.keys()) == {
        "id",
        "position",
        "question_en",
        "question_fr",
        "kind",
        "answers",
        "posts_demo_transaction",
    }
    for option in q["answers"]:
        assert set(option.keys()) == {"option_key", "text_en", "text_fr"}

    # The OPTION TEXTS are legitimately served (learners must see the choices
    # to answer); what is protected is WHICH one is correct. The exact key-set
    # checks above prove no per-option marker reaches the client, so the stored
    # correct option is indistinguishable from its distractors here.
    rows = test_db_session.query(Answer).filter(Answer.question_id == q["id"]).all()
    assert any(a.is_correct for a in rows)  # the key exists server-side for grading
    for row in rows:
        assert row.text_en in raw  # every option visible, none distinguished

    # Sections DO carry their stable id (the Part C1 remediation anchor) plus
    # content — and nothing else.
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

    # Ask a different question so the check is not satisfied by coincidence.
    _lesson, detail6 = _lesson_by_slug(client, "the-trial-balance")
    raw6 = json.dumps(detail6)
    assert "explanation" not in raw6
    assert "is_correct" not in raw6


# --- 8) Part C1 — post-answer feedback content --------------------------------
def test_correct_answer_feedback_explains_in_the_requested_language(
    client, test_db_session
):
    """A correct answer returns the explanation + encouragement, in the language
    asked for — and never a remediation target (there is nothing to review)."""
    _register(client)  # stored preference: 'en'
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]  # mcq
    correct_key, _wrong_key = _answer_keys(test_db_session, q["id"])
    stored = _stored_question(test_db_session, q["id"])
    assert stored.explanation_en and stored.explanation_fr

    en = _attempt(client, lesson["id"], q["id"], lang="en", option_key=correct_key)
    assert en["is_correct"] is True
    fb = en["feedback"]
    assert fb["correct"] is True
    assert fb["explanation"] == stored.explanation_en
    assert fb["encouragement"] == feedback_copy.encouragement("en")
    assert fb["correction"] is None
    assert fb["remediation"] is None

    fr = _attempt(client, lesson["id"], q["id"], lang="fr", option_key=correct_key)
    fb_fr = fr["feedback"]
    assert fb_fr["correct"] is True
    assert fb_fr["explanation"] == stored.explanation_fr
    assert fb_fr["encouragement"] == feedback_copy.encouragement("fr")

    # The two languages genuinely differ (selection is not a no-op).
    assert fb_fr["explanation"] != fb["explanation"]
    assert feedback_copy.encouragement("fr") != feedback_copy.encouragement("en")


def test_incorrect_answer_feedback_explains_and_points_at_a_section(
    client, test_db_session
):
    """An incorrect answer returns the concept explanation, the plain-language
    correction and — when configured — a remediation target in the SAME lesson."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, "the-accounting-equation")
    q = next(x for x in detail["questions"] if x["kind"] == "short_answer")

    # Resolve the remediation target the seed actually nominated (every seeded
    # question has one). Do NOT re-point it here: stored content that drifts
    # from the seed fingerprint is re-synced on the next read, which re-creates
    # question ids — the pointer must stay seed-consistent to stay addressable.
    stored = _stored_question(test_db_session, q["id"])
    assert stored.remediation_section_id is not None
    section = test_db_session.get(LessonSection, stored.remediation_section_id)
    assert section is not None
    test_db_session.expire_all()

    res = _attempt(client, lesson["id"], q["id"], lang="en", text="liabilities")
    assert res["is_correct"] is False
    fb = res["feedback"]
    assert fb["correct"] is False
    assert fb["explanation"] == stored.explanation_en
    assert fb["correction"] == stored.correction_en
    assert fb["encouragement"] is None  # encouragement is a correct-answer thing

    # The action is offered, localized, and scoped to THIS lesson's section.
    rem = fb["remediation"]
    assert rem["lesson_id"] == lesson["id"]
    assert rem["section_id"] == section.id
    assert rem["section_position"] == section.position
    assert rem["section_title"] == section.heading_en
    assert rem["action_label"] == feedback_copy.action_label("en")

    # Lesson scoping is verified against the database, not just trusted.
    owner = test_db_session.get(LessonSection, rem["section_id"])
    assert owner is not None
    assert owner.lesson_id == lesson["id"]

    # French selection localizes the label and the section heading.
    fr = _attempt(client, lesson["id"], q["id"], lang="fr", text="liabilities")
    rem_fr = fr["feedback"]["remediation"]
    assert rem_fr["section_id"] == section.id
    assert rem_fr["action_label"] == feedback_copy.action_label("fr")
    assert rem_fr["section_title"] == section.heading_fr
    assert fr["feedback"]["explanation"] == stored.explanation_fr
    assert fr["feedback"]["correction"] == stored.correction_fr


def test_remediation_target_is_dropped_when_missing_or_foreign():
    """Unit: a missing pointer — or a pointer that is not verifiably part of
    THIS lesson — yields no remediation target. Omitted, never guessed."""
    lesson = SimpleNamespace(
        id=7,
        sections=[
            SimpleNamespace(id=71, position=2, heading_en="Checking the books", heading_fr="Vérifier les livres"),
        ],
    )

    # No pointer configured.
    assert (
        _remediation_target(SimpleNamespace(remediation_section_id=None), lesson, "en")
        is None
    )
    # Stale / foreign pointer: not among this lesson's sections.
    assert (
        _remediation_target(SimpleNamespace(remediation_section_id=999), lesson, "en")
        is None
    )
    # A pointer at this lesson's own section resolves — localized.
    target = _remediation_target(
        SimpleNamespace(remediation_section_id=71), lesson, "fr"
    )
    assert target is not None
    assert target.lesson_id == 7
    assert target.section_id == 71
    assert target.section_position == 2
    assert target.section_title == "Vérifier les livres"
    assert target.action_label == feedback_copy.action_label("fr")


def test_feedback_language_falls_back_to_stored_preference(client):
    """Without an explicit ?lang, the signed-in user's stored language
    preference selects the feedback language (English/French consistency)."""
    _register(client, email="francoise@example.com", name="Françoise", lang="fr")
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]

    no_lang = _attempt(client, lesson["id"], q["id"], option_key="B")  # stored pref: fr
    as_en = _attempt(client, lesson["id"], q["id"], lang="en", option_key="B")
    as_fr = _attempt(client, lesson["id"], q["id"], lang="fr", option_key="B")

    assert no_lang["feedback"]["explanation"] == as_fr["feedback"]["explanation"]
    assert no_lang["feedback"]["explanation"] != as_en["feedback"]["explanation"]
    assert no_lang["is_correct"] is as_en["is_correct"]  # scoring is language-blind


# --- 10) History-preserving lesson synchronization (foreign-key safety) --------

def test_ensure_default_lessons_preserves_answered_attempt(client, test_db_session):
    """A historical attempt survives lesson synchronization intact."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, "the-accounting-equation")
    q = detail["questions"][0]
    correct_key, wrong_key = _answer_keys(test_db_session, q["id"])

    # Submit an answer and get the attempt ID from the database
    _attempt(client, lesson["id"], q["id"], option_key=wrong_key)
    
    # Get the attempt ID from the database (it's the most recent one for this user/question)
    user_id = _signed_in_user(test_db_session).id
    attempt = test_db_session.query(Attempt).filter(
        Attempt.user_id == user_id,
        Attempt.question_id == q["id"]
    ).order_by(Attempt.id.desc()).first()
    attempt_id = attempt.id

    from app.learning.service import ensure_default_lessons

    ensure_default_lessons(test_db_session)
    test_db_session.commit()

    still_exists = (
        test_db_session.query(Attempt)
        .filter(Attempt.id == attempt_id)
        .first()
    )
    assert still_exists is not None


def test_answer_ids_remain_stable_after_sync(client, test_db_session):
    """Answer IDs do not change after lesson synchronization."""
    _register(client)
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    q = detail["questions"][0]

    before = (
        test_db_session.query(Answer)
        .filter(Answer.question_id == q["id"])
        .order_by(Answer.position)
        .all()
    )
    before_ids = [a.id for a in before]

    from app.learning.service import ensure_default_lessons

    ensure_default_lessons(test_db_session)
    test_db_session.commit()

    after = (
        test_db_session.query(Answer)
        .filter(Answer.question_id == q["id"])
        .order_by(Answer.position)
        .all()
    )
    after_ids = [a.id for a in after]

    assert before_ids == after_ids, (
        "Answer IDs changed after synchronization — historical attempts would break"
    )


def test_lesson_sync_is_idempotent(client, test_db_session):
    """Calling ensure_default_lessons() twice does not create duplicates."""
    _register(client)

    from app.learning.service import ensure_default_lessons

    ensure_default_lessons(test_db_session)
    count_after_first = (
        test_db_session.query(Lesson).filter(Lesson.slug == "what-is-accounting").count()
    )
    assert count_after_first == 1

    ensure_default_lessons(test_db_session)
    test_db_session.commit()

    count_after_second = (
        test_db_session.query(Lesson).filter(Lesson.slug == "what-is-accounting").count()
    )
    assert count_after_second == 1
