"""Learning engine tests (Session 11 Part A).

Covers the acceptance points:
1. The 7 lessons seed in the exact ACCA-FIA curriculum order, EN+FR.
2. Lesson detail serves sections + questions per-request; correct answers are
   NOT exposed by the read endpoints (content-protection requirement).
3. Scoring: correct/incorrect MCQ + short-answer straight comparison.
4. Per-user progress roll-up (two users are fully independent).
5. Language toggle respected: every payload carries both en/fr variants.
6. Lesson 4 practice connector posts a REAL balanced transaction into the
   demo workspace end-to-end (and does NOT post on a wrong answer).
"""
from decimal import Decimal


def _register(client, email="learner@example.com", name="Learner", lang="en"):
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


def _attempt(client, lesson_id, question_id, **extra):
    payload = {"lesson_id": lesson_id, "question_id": question_id, **extra}
    r = client.post("/learning/attempts", json=payload)
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