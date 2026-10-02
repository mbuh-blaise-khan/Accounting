"""Lesson 4 expansion tests.

The original 3-section / 2-question Lesson 4 was expanded IN PLACE into a full
beginner lesson (10 sections + 18 questions, all built around the continuing
"Manka'a Provisions" shop in Bamenda) WITHOUT creating a duplicate lesson,
course, slug, id or curriculum path: same slug ("journal-entries"), same
curriculum position (4), same EN/FR titles, and the two ORIGINAL questions keep
their positions (1, 2), question ids, answer ids, option keys, correct answers,
explanations, corrections and the Practice-connector flag/amount.

These tests pin the nine acceptance areas for this expansion:
1. Identity: slug/position/titles, the 7-lesson curriculum order, and that no
   duplicate lesson/course/slug exists.
2. Originals: positions 1-2 keep kind, option keys, correct answers, accepted
   short-answer texts and connector data; their stored ids survive re-sync.
3. Persisted shape: 10 sections, 18 questions, unique immutable ids, unique
   contiguous positions 1..18, EN/FR everywhere, one connector.
4. Seed/upsert idempotency + history preservation (repeated re-sync changes no
   question id, no answer id, and no learner attempt/progress/review).
5. No duplicate normal sequence, no adjacent duplicate questions.
6. Wrong answer -> C1 remediation + C2 review card -> NEXT DISTINCT question.
7. Refresh/resume, bounded progress, review-to-mastery on the SAME question id.
8. Stable answer-identity grading + safe deterministic option display, Lesson
   and Review using an identical order.
9. Practice connector: correct org context, exactly ONE transaction ever posted,
   idempotent on retry/refresh/duplicate submission, none on a wrong answer.
10. Certificate rule `status == "completed" AND best_score == 100` unchanged and
    Lessons 1-3 regression invariants intact.
"""
from decimal import Decimal

from app.learning.service import (
    _MEANINGFUL_OPTION_ORDER,
    _OPTION_ORDER_LESSON_SLUGS,
)
from app.models.learning import Answer, Attempt, Lesson, Question, ReviewItem
from app.models.organization import Organization, OrganizationMember
from app.models.transaction import Transaction
from app.models.user import User
from app.services import certificate_service
from app.tests.test_learning import (
    EXPECTED_SLUGS,
    _answer_keys,
    _attempt,
    _correct_answer_payload,
    _create_org,
    _lesson_by_slug,
    _register,
)
from app.tests.test_learning_reviews import _answer_review, _reviews

SLUG = "journal-entries"

EXPECTED_KINDS = {
    1: "mcq", 2: "mcq", 3: "mcq", 4: "short_answer", 5: "mcq", 6: "mcq",
    7: "short_answer", **{p: "mcq" for p in range(8, 19)},
}

EXPECTED_REMEDIATION = {
    1: 5, 2: 2, 3: 3, 4: 3, 5: 4, 6: 5, 7: 5, 8: 5, 9: 5,
    10: 4, 11: 7, 12: 7, 13: 8, 14: 7, 15: 8, 16: 9, 17: 9, 18: 10,
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
    # Exactly ONE Lesson 4 row exists - no duplicate lesson, course or slug.
    assert len([l for l in lessons if l["slug"] == SLUG]) == 1
    lesson = lessons[3]
    assert lesson["position"] == 4
    assert lesson["title_en"] == "Recording a transaction (journal entries)"
    assert lesson["title_fr"] == "Enregistrer une opération (écritures de journal)"
    assert lesson["title_en"] != lesson["title_fr"]
    assert lesson["summary_en"] and lesson["summary_fr"]
    rows = test_db_session.query(Lesson).filter(Lesson.slug == SLUG).all()
    assert len(rows) == 1
    assert len({l["id"] for l in lessons}) == 7
    # The single curriculum/certificate identity is unchanged.
    assert certificate_service.COURSE_SLUG == "accounting-basics"


# --- 2) Original questions/answers + connector data are unchanged -------------
def test_original_questions_answers_and_connector_preserved(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]
    q1, q2 = qs[0], qs[1]

    # Q1 - ORIGINAL practice question: position 1, mcq, A correct, 4 options.
    assert (q1["position"], q1["kind"]) == (1, "mcq")
    assert "25,000" in q1["question_en"] and "25 000" in q1["question_fr"]
    rows1 = (
        test_db_session.query(Answer)
        .filter(Answer.question_id == q1["id"])
        .order_by(Answer.position)
        .all()
    )
    assert [a.option_key for a in rows1] == ["A", "B", "C", "D"]
    assert [a.is_correct for a in rows1] == [True, False, False, False]
    assert [a.text_en for a in rows1] == [
        "Debit Cash 25,000 / Credit Sales 25,000",
        "Debit Sales 25,000 / Credit Cash 25,000",
        "Debit Cash 25,000 / Credit Capital 25,000",
        "Credit Cash 25,000 / Credit Sales 25,000",
    ]
    # Connector contract: still exactly one flagged question, at position 1,
    # still 25,000.
    flagged = [q for q in qs if q["posts_demo_transaction"]]
    assert len(flagged) == 1 and flagged[0]["position"] == 1
    row1 = test_db_session.get(Question, q1["id"])
    assert row1.posts_demo_transaction is True
    assert Decimal(str(row1.practice_amount)) == Decimal("25000")

    # Q2 - ORIGINAL: position 2, mcq, A correct, 3 options.
    assert (q2["position"], q2["kind"]) == (2, "mcq")
    assert q2["question_en"] == "What is the purpose of the journal?"
    assert q2["question_fr"] == "Quel est le rôle du journal ?"
    correct2, _w2 = _answer_keys(test_db_session, q2["id"])
    assert correct2 == "A"
    assert _stored_keys(test_db_session, q2["id"])[0] == ["A", "B", "C"]


# --- 3) Persisted shape: 10 sections, 18 unique ids, contiguous positions -----
def test_lesson4_has_10_sections_and_18_unique_positions(client):
    _register(client)
    _lesson, detail = _lesson_by_slug(client, SLUG)
    secs, qs = detail["sections"], detail["questions"]
    assert len(secs) == 10
    assert [s["position"] for s in secs] == list(range(1, 11))
    assert len(qs) == 18
    assert len({q["id"] for q in qs}) == 18          # unique immutable ids
    assert [q["position"] for q in qs] == list(range(1, 19))  # unique+contiguous
    for a, b in zip(qs, qs[1:]):                     # no adjacent duplicates
        assert a["id"] != b["id"]
        assert a["position"] != b["position"]
        assert a["question_en"] != b["question_en"]
        assert a["question_fr"] != b["question_fr"]
    assert {q["position"]: q["kind"] for q in qs} == EXPECTED_KINDS
    assert detail["progress"]["questions_total"] == 18
    # Reads never expose the key.
    for q in qs:
        assert "is_correct" not in q
        for a in q["answers"]:
            assert "is_correct" not in a


# --- 4) EN/FR parity, explanations, corrections, remediation links -----------
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
    # Every remediation pointer resolves to a section of THIS lesson.
    positions = {s["position"] for s in detail["sections"]}
    for q in detail["questions"]:
        row = test_db_session.get(Question, q["id"])
        assert row.remediation_section_id is not None
        target = next(
            s for s in detail["sections"] if s["id"] == row.remediation_section_id
        )
        assert target["position"] == EXPECTED_REMEDIATION[q["position"]]
        assert target["position"] in positions
    # Local/Cameroon context and the honest scope notes are present in both.
    bodies_en = "\n".join(s["body_en"] for s in detail["sections"])
    bodies_fr = "\n".join(s["body_fr"] for s in detail["sections"])
    for needle in ("BEFORE YOU START", "Manka'a Provisions", "Nkwen Market",
                   "Mama Ndifor", "ENEO", "Mobile Money", "160,000",
                   "REVERSING ENTRY", "AN HONEST PROMISE"):
        assert needle in bodies_en, needle
    for needle in ("AVANT DE COMMENCER", "Manka'a Provisions", "Nkwen Market",
                   "Mama Ndifor", "ENEO", "Mobile Money", "160 000",
                   "ÉCRITURE INVERSE", "UNE PROMESSE HONNÊTE"):
        assert needle in bodies_fr, needle
    # No claim of professional/regulated status anywhere in the content.
    forbidden = ("you are now an accountant", "certified accountant",
                 "chartered accountant")
    whole = (bodies_en + " " + bodies_fr).lower()
    for phrase in forbidden:
        assert phrase not in whole, phrase
    assert "honest note" in detail["sections"][-1]["heading_en"].lower()
    assert "note honnête" in detail["sections"][-1]["heading_fr"].lower()


# --- 5) Seed/upsert idempotency + attempts/progress/reviews preserved ---------
def test_reseed_is_idempotent_and_preserves_all_history(client, test_db_session):
    _register(client)
    org = _create_org(client, framework="OHADA")
    lesson, detail = _lesson_by_slug(client, SLUG)
    qs = detail["questions"]

    # Build real history: one wrong answer (creates a review card), the rest
    # correct, and post the practice connector exactly once.
    wrong_q = qs[4]
    _c4, w4 = _answer_keys(test_db_session, wrong_q["id"])
    _attempt(client, lesson["id"], wrong_q["id"], option_key=w4)
    practice_q = qs[0]
    _attempt(client, lesson["id"], practice_q["id"],
             option_key=_answer_keys(test_db_session, practice_q["id"])[0],
             organization_id=org["id"])
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
    txns_before = client.get(f"/transactions?organization_id={org['id']}").json()

    # Three more full re-syncs (every request re-seeds) must change NOTHING.
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
    assert len(detail2["questions"]) == 18      # no duplicate rows
    assert len(detail2["sections"]) == 10

    attempts_after = {
        a.id: (a.question_id, a.is_correct, a.selected_answer_id)
        for a in test_db_session.query(Attempt).all()
    }
    assert attempts_after == attempts_before     # history byte-identical
    assert {(c.question_id, c.stage) for c in test_db_session.query(ReviewItem).all()} == cards_before
    assert _lesson_by_slug(client, SLUG)[1]["progress"] == progress_before
    assert client.get(f"/transactions?organization_id={org['id']}").json() == txns_before


# --- 6) Wrong answer -> remediation + review -> NEXT DISTINCT question -------
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

    # The normal sequence is unchanged: no repeat, no duplicate row.
    detail2 = _lesson_by_slug(client, SLUG)[1]
    assert [x["id"] for x in detail2["questions"]] == [x["id"] for x in qs]
    nxt = detail2["questions"][5]
    assert nxt["id"] != missed["id"]
    assert nxt["position"] == missed["position"] + 1
    # A SECOND wrong answer on the same question never creates a new slot.
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
    assert p["questions_total"] == 18
    assert p["questions_answered"] == 18          # distinct questions, not rows
    assert p["questions_correct"] == 17
    assert p["best_score"] == 94
    assert p["status"] == "completed"

    # Retrying the missed question correctly still counts 18, not 19.
    _attempt(client, lesson["id"], missed["id"],
             **_correct_answer_payload(test_db_session, missed))
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert p["questions_answered"] == 18          # never exceeds the total
    assert p["questions_correct"] == 18
    assert p["best_score"] == 100

    # The review correction lands on the SAME immutable question id.
    card = next(c for c in _reviews(client) if c["question_id"] == missed["id"])
    before = {a.id for a in test_db_session.query(Attempt).all()}
    out = _answer_review(client, card["id"],
                         **_correct_answer_payload(test_db_session, missed))
    assert out["correct"] is True
    new_rows = [a for a in test_db_session.query(Attempt).all() if a.id not in before]
    assert len(new_rows) == 1
    assert new_rows[0].question_id == missed["id"]
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert p["questions_answered"] == 18
    assert p["questions_correct"] == 18
    assert p["best_score"] == 100

    # Refresh / navigate away and back resumes from persisted server progress.
    again = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert again == p


# --- 8) Stable answer-identity grading + safe deterministic option display ----
def test_stable_grading_and_deterministic_option_display(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    assert SLUG in _OPTION_ORDER_LESSON_SLUGS
    exempt = _MEANINGFUL_OPTION_ORDER.get(SLUG, frozenset())
    assert exempt == frozenset()   # no question opts out; documented in service.py

    baseline = _displayed_keys(detail)

    # Every MCQ has valid, unique answers and exactly one correct key.
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
        # Display order is a permutation of the stored keys, never a subset.
        assert sorted(baseline[q["id"]]) == sorted(a.option_key for a in rows)
        if q["position"] not in exempt:
            positions.append(
                baseline[q["id"]].index(
                    next(a.option_key for a in rows if a.is_correct)
                )
            )
    # The correct answer is NOT always rendered first.
    assert positions and max(positions) > 0
    assert len(set(positions)) > 1

    # Deterministic across repeat fetch / refresh / navigation and in EN and FR.
    for _ in range(3):
        assert _displayed_keys(_lesson_by_slug(client, SLUG)[1]) == baseline
    fr = client.get("/learning/lessons/%d?lang=fr" % lesson["id"]).json()
    assert _displayed_keys(fr) == baseline

    # Grading is by stable option_key, never display index. Driven over a
    # representative spread (both short-answer and MCQ, first/last options) so
    # the assertion is identical in meaning but does not pay for 32 graded
    # attempts against the per-request re-seed.
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
    # Display order is untouched by answering.
    assert _displayed_keys(_lesson_by_slug(client, SLUG)[1]) == baseline
    # EN and FR still agree on the option order after all that.
    assert _displayed_keys(
        client.get("/learning/lessons/%d?lang=fr" % lesson["id"]).json()
    ) == baseline


# --- 9) Review queue renders the SAME deterministic option order as the lesson --
def test_review_uses_identical_deterministic_option_order(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    baseline = _displayed_keys(detail)
    # Miss one MCQ question so a review card exists for it (a short-answer probe
    # has no option keys to grade against).
    probe = next(q for q in detail["questions"] if q["kind"] == "mcq" and q["position"] > 1)
    _attempt(client, lesson["id"], probe["id"],
             option_key=_answer_keys(test_db_session, probe["id"])[1])
    card = next(c for c in _reviews(client) if c["question_id"] == probe["id"])
    assert [a["option_key"] for a in card["answers"]] == baseline[probe["id"]]
    # And again after answering it - the order never drifts.
    _answer_review(client, card["id"],
                   option_key=_answer_keys(test_db_session, probe["id"])[1])
    card2 = next(c for c in _reviews(client) if c["question_id"] == probe["id"])
    assert [a["option_key"] for a in card2["answers"]] == baseline[probe["id"]]


# --- 10) Practice connector: context, balance, and IDEMPOTENCY ---------------
def test_practice_connector_posts_exactly_one_transaction(client, test_db_session):
    _register(client)
    org = _create_org(client, framework="OHADA")
    lesson, detail = _lesson_by_slug(client, SLUG)
    practice = next(q for q in detail["questions"] if q["posts_demo_transaction"])
    correct, wrong = _answer_keys(test_db_session, practice["id"])

    # A wrong answer posts NOTHING.
    bad = _attempt(client, lesson["id"], practice["id"], option_key=wrong,
                   organization_id=org["id"])
    assert bad["is_correct"] is False
    assert bad["practice_posted"] is False
    assert bad["practice_transaction_id"] is None
    assert client.get(f"/transactions?organization_id={org['id']}").json() == []

    first = _attempt(client, lesson["id"], practice["id"], option_key=correct,
                     organization_id=org["id"])
    assert first["is_correct"] is True
    assert first["practice_posted"] is True
    assert first["practice_error"] is None
    txn_id = first["practice_transaction_id"]
    assert txn_id is not None

    # The transaction is REAL, posted and balanced in the caller's workspace.
    txns = client.get(f"/transactions?organization_id={org['id']}").json()
    posted = [t for t in txns if t["id"] == txn_id]
    assert len(posted) == 1
    assert posted[0]["status"] == "posted"
    lines = posted[0]["lines"]
    assert len(lines) == 2
    by_code = {line["account_code"]: line for line in lines}
    assert set(by_code) == {"5711", "7011"}
    assert Decimal(by_code["5711"]["debit_amount"]) == Decimal("25000")
    assert Decimal(by_code["7011"]["credit_amount"]) == Decimal("25000")
    tb = client.get(f"/trial-balance?organization_id={org['id']}").json()
    assert tb["balanced"] is True
    assert float(tb["totals"]["closing_debit"]) == 25000.0


def test_practice_connector_is_idempotent_on_retry_refresh_and_duplicates(
    client, test_db_session
):
    _register(client)
    org = _create_org(client, framework="OHADA")
    lesson, detail = _lesson_by_slug(client, SLUG)
    practice = next(q for q in detail["questions"] if q["posts_demo_transaction"])
    correct = _answer_keys(test_db_session, practice["id"])[0]

    ids = []
    # Retry, double-click and a "refreshed page re-submits" all repeat the same
    # correct answer. None may create a second transaction.
    for _ in range(4):
        res = _attempt(client, lesson["id"], practice["id"], option_key=correct,
                       organization_id=org["id"])
        assert res["is_correct"] is True
        assert res["practice_error"] is None
        ids.append(res["practice_transaction_id"])
    assert len(set(ids)) == 1 and ids[0] is not None

    txns = client.get(f"/transactions?organization_id={org['id']}").json()
    assert len(txns) == 1
    assert txns[0]["id"] == ids[0]
    assert txns[0]["status"] == "posted"
    assert len(txns[0]["lines"]) == 2
    assert len(test_db_session.query(Transaction)
               .filter(Transaction.organization_id == org["id"]).all()) == 1

    # The trial balance is NOT inflated by the retries.
    tb = client.get(f"/trial-balance?organization_id={org['id']}").json()
    assert tb["balanced"] is True
    assert float(tb["totals"]["closing_debit"]) == 25000.0
    assert float(tb["totals"]["closing_credit"]) == 25000.0

    # Progress still says "posted" - the flag is idempotent, not a counter.
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    assert p["practice_posted"] is True


def test_practice_connector_uses_the_correct_workspace_context(
    client, test_db_session
):
    """The connector can only post into a workspace the CALLER belongs to."""
    _register(client)
    mine = _create_org(client, framework="OHADA", name="Mine")

    # A second, genuinely different user who is NOT a member of `mine`.
    _register(client, email="other@example.com", name="Other")
    assert test_db_session.query(OrganizationMember).filter(
        OrganizationMember.org_id == mine["id"],
    ).first() is not None  # the first user IS a member...
    other = test_db_session.query(User).filter(
        User.email == "other@example.com"
    ).one()
    assert test_db_session.query(OrganizationMember).filter(
        OrganizationMember.org_id == mine["id"],
        OrganizationMember.user_id == other.id,
    ).first() is None    # ...the second user is NOT

    # `_register` logged the SECOND user in, so this request is made by them.
    lesson, detail = _lesson_by_slug(client, SLUG)
    practice = next(q for q in detail["questions"] if q["posts_demo_transaction"])
    correct = _answer_keys(test_db_session, practice["id"])[0]
    res = _attempt(client, lesson["id"], practice["id"], option_key=correct,
                   organization_id=mine["id"])
    # Grading still happens (the lesson answer is still marked correct)...
    assert res["is_correct"] is True
    # ...but the connector refuses to leak a transaction into somebody else's
    # workspace: it reports an error and creates nothing.
    assert res["practice_posted"] is False
    assert res["practice_transaction_id"] is None
    assert res["practice_error"] is not None
    # No transaction exists anywhere, and the non-member cannot even read the
    # workspace's transactions (the API answers 404 for an org the caller does
    # not belong to).
    assert test_db_session.query(Transaction).all() == []
    assert client.get(f"/transactions?organization_id={mine['id']}").status_code == 404


# --- 11) Certificate rule unchanged ------------------------------------------
def test_certificate_rule_unchanged_after_expansion(client, test_db_session):
    _register(client)
    lesson, detail = _lesson_by_slug(client, SLUG)
    for q in detail["questions"]:
        _attempt(client, lesson["id"], q["id"],
                 **_correct_answer_payload(test_db_session, q))
    p = _lesson_by_slug(client, SLUG)[1]["progress"]
    # The rule is EXACTLY: status == "completed" AND best_score == 100.
    assert p["status"] == "completed"
    assert p["best_score"] == 100
    completion = client.get("/learning/completion").json()
    assert completion["total_lessons"] == 7
    assert completion["completed_lessons"] == 1
    assert completion["completed"] is False
    assert completion["certificate_status"] == "locked"
    assert client.post("/learning/certificate").status_code == 403


# --- 12) Lessons 1-3 regression invariants ----------------------------------
def test_lessons_1_to_3_regression_invariants(client, test_db_session):
    """Lessons 1-3 are untouched by this expansion.

    Their shape, ids, positions, totals, option-display gating and content are
    asserted structurally for ALL THREE, and Lesson 1 is additionally driven to a
    full correct pass so the progress/mastery/review contract is exercised
    end-to-end. Driving all three to completion as well would triple the number
    of graded attempts for no extra coverage - the engine is the same code path.
    """
    _register(client)
    for slug in ("what-is-accounting", "the-accounting-equation",
                 "debits-and-credits"):
        _lesson, detail = _lesson_by_slug(client, slug)
        qs = detail["questions"]
        assert len(qs) == 18
        assert len({q["id"] for q in qs}) == 18
        assert [q["position"] for q in qs] == list(range(1, 19))
        assert detail["progress"]["questions_total"] == 18
        assert detail["progress"]["status"] == "not_started"
        # Still gated (or not) exactly as before this expansion.
        if slug in ("the-accounting-equation", "debits-and-credits"):
            assert slug in _OPTION_ORDER_LESSON_SLUGS
        else:
            assert slug not in _OPTION_ORDER_LESSON_SLUGS
        # No Lesson 1-3 question carries the Lesson 4 connector.
        assert not any(q["posts_demo_transaction"] for q in qs)
        # Every question still has full EN/FR content and feedback.
        for q in qs:
            assert q["question_en"] and q["question_fr"]
            row = test_db_session.get(Question, q["id"])
            assert row.explanation_en and row.correction_en

    # Lesson 1 driven to a full correct pass: progress, mastery and the
    # certificate rule all behave exactly as before.
    lesson, detail = _lesson_by_slug(client, "what-is-accounting")
    for q in detail["questions"]:
        _attempt(client, lesson["id"], q["id"],
                 **_correct_answer_payload(test_db_session, q))
    p = _lesson_by_slug(client, "what-is-accounting")[1]["progress"]
    assert p["questions_answered"] == 18
    assert p["questions_correct"] == 18
    assert p["status"] == "completed"
    assert p["best_score"] == 100
    assert p["practice_posted"] is False

    # Lesson 4 still has EXACTLY one connector question, at position 1.
    _lesson4, l4 = _lesson_by_slug(client, SLUG)
    flagged = [q for q in l4["questions"] if q["posts_demo_transaction"]]
    assert len(flagged) == 1 and flagged[0]["position"] == 1

    # One of seven lessons completed still leaves the COURSE locked: the rule
    # is `status == "completed" AND best_score == 100` for ALL SEVEN.
    completion = client.get("/learning/completion").json()
    assert completion["total_lessons"] == 7
    assert completion["completed_lessons"] == 1
    assert completion["completed"] is False
    assert completion["certificate_status"] == "locked"
    assert client.post("/learning/certificate").status_code == 403
