"""Learning engine service (Session 11 Part A + Part C1).

- `ensure_default_lessons` seeds the 7-curriculum lessons idempotently.
- `list_lessons` / `get_lesson` serve content per-request with the user's
  progress rolled up. Correct answers and the Part C1 explanations/corrections
  are NEVER exposed by these reads.
- `submit_attempt` scores by STRAIGHT COMPARISON (no AI), records the
  attempt, rolls up `progress`, — for the Lesson 4 practice connector —
  posts a REAL balanced transaction into the user's demo workspace when the
  answer is correct and an organization_id was supplied, and returns the
  Part C1 learner-safe `feedback` object (explanation / correction /
  encouragement / optional remediation target) in the learner's language.

Deterministic engine rule (see .clinerules): nothing here decides a
debit/credit outcome with AI. The practice posting uses fixed, balanced
double-entry lines against the org's own chart (Cash Dr / Sales Cr).
"""
import hashlib
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.learning import feedback as feedback_copy
from app.learning.schemas import (
    AnswerFeedbackOut,
    AttemptOut,
    LessonDetailOut,
    LessonProgressOut,
    LessonSectionOut,
    LessonSummaryOut,
    QuestionAnswerOut,
    QuestionOut,
    RemediationOut,
    ReviewAnswerOut,
    ReviewItemOut,
    ReviewSummaryOut,
)
from app.learning.seed_data import LESSONS
from app.models.account import Account
from app.models.learning import (
    Answer,
    Attempt,
    Lesson,
    LessonProgress,
    LessonSection as LessonSectionModel,
    Question,
    ReviewItem,
)
from app.models.user import User
from app.models.transaction import Transaction
from app.services import posting_service, transaction_service
from app.services.organization_service import get_organization_for_user

#: Immutable marker of the connector's posting intent. It is part of the posted
#: transaction's plain-language description, so an existing practice transaction
#: stays recognisable forever (posted records are never edited or deleted).
_PRACTICE_DESCRIPTION = "Learn Mode: cash sale posted from Lesson 4 practice"


def _existing_practice_post(
    db: Session, user: User, question: Question, org_id: int
) -> int | None:
    """The transaction id this user ALREADY got from this connector, or None.

    IDEMPOTENCY GUARD (Lesson 4 expansion). `submit_attempt` is reachable from a
    retry, a double-click, a duplicate submission or a refreshed page that
    re-submits the same correct answer. Without this guard, each of those would
    post ANOTHER balanced cash sale into the user's own workspace and quietly
    inflate their trial balance - the connector would be the one place in this
    platform where the same business event could be counted twice.

    The lookup is by IMMUTABLE IDENTITY - (user, question id, organization id) -
    never by position, never by date and never by a caller-supplied flag, so a
    re-seed, a re-order or a renamed question cannot re-arm the connector. Only a
    transaction that still EXISTS is returned: if the workspace was deleted or
    the posting was rolled back, `None` is returned and the connector posts
    afresh, which is correct behaviour rather than a dangling reference.
    """
    prior = (
        db.query(Attempt)
        .filter(
            Attempt.user_id == user.id,
            Attempt.question_id == question.id,
            Attempt.organization_id == org_id,
            Attempt.practice_posted.is_(True),
            Attempt.practice_transaction_id.isnot(None),
        )
        .order_by(Attempt.id.asc())
        .all()
    )
    for attempt in prior:
        txn = db.get(Transaction, attempt.practice_transaction_id)
        if txn is not None:
            return txn.id
    return None

# --- Assessment-quality option display order (Lesson 2 hotfix) ----------------
#
# ROOT CAUSE: `Question.answers` is loaded `ORDER BY position`, i.e. straight
# from seed order, and both read paths (`get_lesson` and `_review_item_out`)
# serialized that list verbatim. In Lesson 2 every closed-ended question was
# authored with `is_correct: True` on the FIRST option, so the correct answer
# was rendered in displayed position 1 for EVERY question — a positional
# pattern a learner can exploit without understanding the accounting.
#
# FIX (deterministic, display-only): the stored answer rows are never touched.
# Only the ORDER OF THE SERIALIZED LIST changes, computed from the immutable
# `questions.id` and `answers.id` — never from a clock, a random seed or the
# user's session — so the same question always renders the same option order on
# first render, refresh, navigation away/back, retry, feedback, the review queue
# and both EN/FR renderings. `option_key` values are unchanged, and grading
# still resolves the submitted `option_key` to its `Answer` row by id in
# `_score_submission`, so correctness, attempts, review items, progress,
# remediation and the certificate rule are all unaffected.
#
# MEANINGFUL-ORDER EXCEPTION: an option list can have a genuine intrinsic order
# (a sequence, a timeline, ascending values the learner must read in order).
# Shuffling those harms comprehension, so they are exempt. `_MEANINGFUL_...`
# below is the documented exemption list, keyed by lesson slug -> the question
# POSITIONS whose options keep their seeded order.
#   - Lesson 2: none. Its numeric options (Q1, Q7, Q12, Q13, Q14) are competing
#     answers to "what is the figure", not a sequence whose order is being
#     tested, so reordering them improves assessment integrity without harming
#     comprehension.
#   - Lesson 3 (`debits-and-credits`): none, and this was checked explicitly.
#     Every closed-ended question there offers ALTERNATIVE candidate entries or
#     statements, so the order of the options never conveys the answer; the
#     lesson contains no "list these steps in order", no chronological sequence
#     and no ordered list whose sequence IS the correct answer. The order that
#     matters (debit side vs credit side) lives INSIDE each option's text
#     ("Dr X / Cr Y"), which the permutation never touches.
#   - Lesson 4 (`journal-entries`): none, and this was checked explicitly. Every
#     closed-ended question there offers ALTERNATIVE candidate entries,
#     documents, dates, narrations, amounts or statements - never a set whose
#     order IS the answer. The lesson contains no "list these steps in order"
#     question: the four analysis steps and the five parts of an entry are taught
#     in the SECTION BODY prose (which the engine never reorders), never as
#     options the learner is asked to read in sequence. Amount options such as
#     "145,000 / 155,000 / 160,000 / 175,000" are competing answers to "what is
#     the figure", not an ascending sequence being tested. The order that matters
#     (Dr vs Cr, date vs narration) lives INSIDE each option's text, which the
#     permutation never touches.
# The mechanism is kept so a future genuinely ordered question can opt out by
# adding its position here.
_OPTION_ORDER_LESSON_SLUGS = frozenset({
    "the-accounting-equation",
    "debits-and-credits",
    "journal-entries",
})
_MEANINGFUL_OPTION_ORDER: dict[str, frozenset[int]] = {
    "the-accounting-equation": frozenset(),
    "debits-and-credits": frozenset(),
    "journal-entries": frozenset(),
}


def _stable_rank(*parts: object) -> int:
    """A process-stable integer derived from `parts`.

    Uses BLAKE2b, not Python's built-in `hash()`, because `hash()` of a str is
    randomized per process (PYTHONHASHSEED) and would give a different option
    order after every server restart — i.e. non-deterministic across refreshes.
    """
    joined = "\x1f".join(str(p) for p in parts)
    digest = hashlib.blake2b(joined.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def _display_answers(question: Question, lesson_slug: str) -> list[Answer]:
    """The option rows to SERIALIZE for one question, in display order.

    Returns a NEW list; the ORM collection is never mutated, so the stored
    `answers.position`, `option_key`, `is_correct` and every attempt/review row
    that references an `answers.id` are untouched.
    """
    answers = list(question.answers)  # stored order (position, id) — untouched
    if question.kind != "mcq" or len(answers) < 2:
        return answers
    if lesson_slug not in _OPTION_ORDER_LESSON_SLUGS:
        return answers
    if question.position in _MEANINGFUL_OPTION_ORDER.get(lesson_slug, frozenset()):
        return answers  # documented meaningful-order exemption

    # Seed from the immutable question id and the immutable answer ids, so the
    # permutation is a pure function of stored identity: identical on every
    # fetch, in both languages, and in the review queue (same question id).
    seed = (question.id, tuple(sorted(a.id for a in answers)))
    n = len(answers)
    order = list(range(n))
    # Deterministic Fisher-Yates: every swap is drawn from the stable rank, and
    # ties fall back to the previous index order, so a collision can never make
    # the result depend on dict/list iteration order.
    for i in range(n - 1, 0, -1):
        j = _stable_rank(seed, "swap", i) % (i + 1)
        order[i], order[j] = order[j], order[i]
    return [answers[i] for i in order]


def _normalise(text: str) -> str:
    return (text or "").strip().lower()


def _progress_dict(user: User, lesson: Lesson, row: LessonProgress | None) -> dict:
    total = len(_normal_questions(lesson))
    if row is None:
        return {
            "status": "not_started",
            "best_score": 0,
            "questions_total": total,
            "questions_answered": 0,
            "questions_correct": 0,
            "practice_posted": False,
        }
    return {
        "status": row.status,
        "best_score": row.best_score,
        "questions_total": total,
        "questions_answered": row.questions_answered,
        "questions_correct": row.questions_correct,
        "practice_posted": row.practice_posted,
    }


def _normal_questions(lesson: Lesson) -> list[Question]:
    """The lesson's FIXED normal sequence: one row per seeded position.

    Deduplicates by immutable question id AND by seeded position (first row
    per position wins, ties broken by id) and returns them in ascending
    position order. This is the single authority for "the normal lesson
    sequence" — progress totals, the detail payload and every downstream
    counter derive from it, so a legacy row duplicated at the same position
    can never be served twice or counted twice (Session 18 hotfix). Review
    cards never appear here; they live only on their own endpoints.
    """
    out: list[Question] = []
    seen_ids: set[int] = set()
    seen_positions: set[int] = set()
    for q in sorted(lesson.questions, key=lambda x: (x.position, x.id)):
        if q.id in seen_ids or q.position in seen_positions:
            continue
        seen_ids.add(q.id)
        seen_positions.add(q.position)
        out.append(q)
    return out


def _heal_duplicate_question_positions(db: Session) -> int:
    """Renumber legacy questions sharing a position (never delete rows).

    Session 18 root-cause fix: two concurrent seed runs (multi-worker startup)
    could each insert the same position, leaving a lesson with duplicated
    question rows — the dev database served Lesson 1 positions 3-10 twice
    ("Question 3 == Question 4" in the UI: 18 rows for 10 seeded questions).
    The lowest-id row per position is canonical and keeps its position; every
    duplicate is RENUMBERED to the next free position. Question ids, answer
    ids, attempts and review cards are all untouched, so history keeps its
    referential integrity — positions are seeded order metadata only.

    Deterministic and idempotent: a healed database performs no writes. It
    runs BEFORE the seed upsert so a renumbered row picks up the seed content
    for its new position in place (dev rows renumbered to 11-18 receive seed
    questions 11-18 on the same ids, keeping every attempt and review card).
    Returns the number of rows renumbered.
    """
    renumbered = 0
    for lesson in db.query(Lesson).all():
        ordered = sorted(lesson.questions, key=lambda x: (x.position, x.id))
        taken: set[int] = set()
        duplicates: list[Question] = []
        for q in ordered:
            if q.position not in taken:
                taken.add(q.position)
            else:
                duplicates.append(q)
        if not duplicates:
            continue
        next_free = 1
        for q in duplicates:
            while next_free in taken:
                next_free += 1
            q.position = next_free
            taken.add(next_free)
            next_free += 1
            renumbered += 1
    if renumbered:
        db.flush()
    return renumbered


def ensure_default_lessons(db: Session) -> None:
    """Idempotent, history-preserving seed: create/update the 7-lesson curriculum
    by slug.

    Existing lessons, questions, and answers keep their IDs. Content fields
    (including Part C1 explanations/corrections/remediation pointers) are
    updated in place when they differ from the seed. New questions/answers are
    inserted only when they don't already exist. Rows that are no longer in the
    seed are left in place (never deleted) so historical attempts keep their
    referential integrity.

    Safe to call on every startup / request / test setup. Unlike the previous
    delete-orphan re-sync, this version never removes answers that historical
    attempts may reference, so FK violations on attempts.selected_answer_id are
    impossible.
    """
    # Session 18: heal legacy duplicate positions BEFORE the upsert so each
    # seed position maps to exactly one row (see the helper's docstring).
    _heal_duplicate_question_positions(db)
    for data in LESSONS:
        lesson = db.query(Lesson).filter(Lesson.slug == data["slug"]).first()
        if lesson is None:
            lesson = Lesson(
                slug=data["slug"],
                position=data["position"],
                title_en=data["title_en"],
                title_fr=data["title_fr"],
                summary_en=data["summary_en"],
                summary_fr=data["summary_fr"],
            )
            db.add(lesson)
            db.flush()
        else:
            lesson.position = data["position"]
            lesson.title_en = data["title_en"]
            lesson.title_fr = data["title_fr"]
            lesson.summary_en = data["summary_en"]
            lesson.summary_fr = data["summary_fr"]

        # Sections: upsert by (lesson_id, position). Leave unseen sections in
        # place -- they are never deleted, so any attempt/refs they own stay valid.
        for sec_data in data["sections"]:
            existing_sec = next(
                (s for s in lesson.sections if s.position == sec_data["position"]), None
            )
            if existing_sec:
                existing_sec.heading_en = sec_data.get("heading_en")
                existing_sec.heading_fr = sec_data.get("heading_fr")
                existing_sec.body_en = sec_data["body_en"]
                existing_sec.body_fr = sec_data["body_fr"]
            else:
                new_sec = LessonSectionModel(
                    position=sec_data["position"],
                    heading_en=sec_data.get("heading_en"),
                    heading_fr=sec_data.get("heading_fr"),
                    body_en=sec_data["body_en"],
                    body_fr=sec_data["body_fr"],
                )
                lesson.sections.append(new_sec)

        # Questions: upsert by (lesson_id, position). Leave unseen questions in
        # place -- they are never deleted, so their answers (and any attempts that
        # reference those answers) stay intact.
        for q_data in data["questions"]:
            existing_q = next(
                (q for q in lesson.questions if q.position == q_data["position"]), None
            )
            if existing_q:
                existing_q.question_en = q_data["question_en"]
                existing_q.question_fr = q_data["question_fr"]
                existing_q.kind = q_data["kind"]
                existing_q.explanation_en = q_data.get("explanation_en")
                existing_q.explanation_fr = q_data.get("explanation_fr")
                existing_q.correction_en = q_data.get("correction_en")
                existing_q.correction_fr = q_data.get("correction_fr")
                existing_q.short_answer_en = q_data.get("short_answer_en")
                existing_q.short_answer_fr = q_data.get("short_answer_fr")
                existing_q.posts_demo_transaction = q_data.get(
                    "posts_demo_transaction", False
                )
                existing_q.practice_amount = q_data.get("practice_amount")
            else:
                existing_q = Question(
                    position=q_data["position"],
                    question_en=q_data["question_en"],
                    question_fr=q_data["question_fr"],
                    kind=q_data["kind"],
                    explanation_en=q_data.get("explanation_en"),
                    explanation_fr=q_data.get("explanation_fr"),
                    correction_en=q_data.get("correction_en"),
                    correction_fr=q_data.get("correction_fr"),
                    short_answer_en=q_data.get("short_answer_en"),
                    short_answer_fr=q_data.get("short_answer_fr"),
                    posts_demo_transaction=q_data.get("posts_demo_transaction", False),
                    practice_amount=q_data.get("practice_amount"),
                )
                lesson.questions.append(existing_q)

            # Answers: upsert by (question_id, option_key). Leave unseen answers
            # in place -- they are never deleted, preserving any historical attempt
            # whose selected_answer_id points at them.
            for a_data in q_data.get("answers", []):
                existing_answer = next(
                    (
                        a for a in existing_q.answers
                        if a.option_key == a_data["option_key"]
                    ),
                    None,
                )
                if existing_answer:
                    existing_answer.position = a_data["position"]
                    existing_answer.text_en = a_data["text_en"]
                    existing_answer.text_fr = a_data["text_fr"]
                    existing_answer.is_correct = a_data.get("is_correct", False)
                else:
                    new_answer = Answer(
                        option_key=a_data["option_key"],
                        position=a_data["position"],
                        text_en=a_data["text_en"],
                        text_fr=a_data["text_fr"],
                        is_correct=a_data.get("is_correct", False),
                    )
                    existing_q.answers.append(new_answer)

        # Flush to get section IDs for remediation pointers
        db.flush()
        sections_by_position = {s.position: s for s in lesson.sections}

        # Set remediation pointers for questions in the seed
        for q_data in data["questions"]:
            question = next(
                (q for q in lesson.questions if q.position == q_data["position"]),
                None,
            )
            if question is None:
                continue
            position = q_data.get("remediation_section_position")
            if position is None:
                continue
            section = sections_by_position.get(position)
            if section is not None:
                question.remediation_section_id = section.id

    # Sync question feedback for DBs seeded before Part C1 (redundant with the
    # upsert above for most rows, but harmless and acts as a safety net).
    _sync_question_feedback(db)
    db.commit()


def _sync_question_feedback(db: Session) -> None:
    """Re-apply Part C1 feedback content to already-stored questions.

    A database seeded before Part C1 (or only partially seeded) has no
    corrections and no remediation pointers. This pass copies the authored seed
    content onto the existing question rows, matching by lesson slug + question
    position so primary keys — and therefore the question ids the client just
    received from the detail endpoint — stay untouched. Every assignment is
    guarded by an equality check, so a fully-synced database performs no writes.

    Remediation pointers are resolved from the lesson's OWN sections, so a
    target can never end up pointing at another lesson.
    """
    for data in LESSONS:
        lesson = db.query(Lesson).filter(Lesson.slug == data["slug"]).first()
        if lesson is None:
            continue
        sections_by_position = {s.position: s for s in lesson.sections}
        questions_by_position = {q.position: q for q in lesson.questions}
        for seed_question in data["questions"]:
            question = questions_by_position.get(seed_question["position"])
            if question is None:
                continue
            correction_en = seed_question.get("correction_en")
            if correction_en and question.correction_en != correction_en:
                question.correction_en = correction_en
                question.correction_fr = seed_question.get("correction_fr")
            section = sections_by_position.get(
                seed_question.get("remediation_section_position")
            )
            target_id = section.id if section is not None else None
            if question.remediation_section_id != target_id:
                question.remediation_section_id = target_id


def _data_fingerprint(data: dict) -> str:
    """Stable fingerprint of the seed-data content for one lesson."""
    secs = "|".join(
        f'{s["position"]}::{s["body_en"]}'
        for s in sorted(data["sections"], key=lambda x: x["position"])
    )
    qparts = []
    for q in sorted(data["questions"], key=lambda x: x["position"]):
        answers = ",".join(
            f'{a["option_key"]}={int(bool(a.get("is_correct", False)))}'
            for a in sorted(q.get("answers", []), key=lambda x: x["position"])
        )
        qparts.append(
            f'{q["position"]}::{q["kind"]}::{q["question_en"]}'
            f'::{q.get("short_answer_en") or ""}'
            f'::{bool(q.get("posts_demo_transaction", False))}::{answers}'
            # Part C1: feedback content participates in the fingerprint, so a
            # database seeded before C1 (no corrections / no remediation
            # pointers) is re-synced once on the next request.
            f'::{q.get("correction_en") or ""}'
            f'::{q.get("remediation_section_position") or ""}'
        )
    return secs + "###" + "||".join(qparts)


def _lesson_fingerprint(lesson: Lesson) -> str:
    """Stable fingerprint of the stored content for one lesson (same shape)."""
    secs = "|".join(
        f"{s.position}::{s.body_en}"
        for s in sorted(lesson.sections, key=lambda x: x.position)
    )
    qparts = []
    # Part C1: remediation pointers are compared by the section's position
    # inside this lesson (ids are assigned at flush time, so positions are the
    # stable equivalent across a re-seed).
    section_positions = {s.id: s.position for s in lesson.sections}
    for q in sorted(lesson.questions, key=lambda x: x.position):
        answers = ",".join(
            f"{a.option_key}={int(bool(a.is_correct))}"
            for a in sorted(q.answers, key=lambda x: x.position)
        )
        qparts.append(
            f"{q.position}::{q.kind}::{q.question_en}"
            f"::{q.short_answer_en or ''}"
            f"::{bool(q.posts_demo_transaction)}::{answers}"
            f"::{q.correction_en or ''}"
            f"::{section_positions.get(q.remediation_section_id) or ''}"
        )
    return secs + "###" + "||".join(qparts)


def _content_differs(lesson: Lesson, data: dict) -> bool:
    return _lesson_fingerprint(lesson) != _data_fingerprint(data)


def list_lessons(db: Session, user: User) -> list[LessonSummaryOut]:
    """All lessons in curriculum order, each with the user's progress."""
    ensure_default_lessons(db)
    lessons = db.query(Lesson).order_by(Lesson.position.asc()).all()
    progress_rows = {
        p.lesson_id: p
        for p in db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id)
        .all()
    }
    out = []
    for lesson in lessons:
        out.append(
            LessonSummaryOut(
                id=lesson.id,
                slug=lesson.slug,
                position=lesson.position,
                title_en=lesson.title_en,
                title_fr=lesson.title_fr,
                summary_en=lesson.summary_en,
                summary_fr=lesson.summary_fr,
                progress=LessonProgressOut(**_progress_dict(user, lesson, progress_rows.get(lesson.id))),
            )
        )
    return out
def get_lesson(db: Session, user: User, lesson_id: int) -> LessonDetailOut:
    """Full lesson content + the user's progress.

    Correct-answer flags are NEVER returned here — only the scoring
    endpoint (server-side) reveals them after an attempt.
    """
    ensure_default_lessons(db)
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )
    row = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.user_id == user.id,
            LessonProgress.lesson_id == lesson.id,
        )
        .first()
    )
    return LessonDetailOut(
        id=lesson.id,
        slug=lesson.slug,
        position=lesson.position,
        title_en=lesson.title_en,
        title_fr=lesson.title_fr,
        summary_en=lesson.summary_en,
        summary_fr=lesson.summary_fr,
        sections=[
            LessonSectionOut(
                id=s.id,
                position=s.position,
                heading_en=s.heading_en,
                heading_fr=s.heading_fr,
                body_en=s.body_en,
                body_fr=s.body_fr,
            )
            for s in lesson.sections
        ],
        questions=[
            QuestionOut(
                id=q.id,
                position=q.position,
                question_en=q.question_en,
                question_fr=q.question_fr,
                kind=q.kind,
                answers=[
                    QuestionAnswerOut(
                        option_key=a.option_key,
                        text_en=a.text_en,
                        text_fr=a.text_fr,
                    )
                    for a in _display_answers(q, lesson.slug)
                ],
                posts_demo_transaction=q.posts_demo_transaction,
            )
            for q in _normal_questions(lesson)
        ],
        progress=LessonProgressOut(**_progress_dict(user, lesson, row)),
    )


def _apply_practice_posting(
    db: Session, user: User, question: Question, org_id: int, amount
) -> tuple[int | None, str | None]:
    """Lesson 4 connector: post the fixed, balanced cash-sale entry.

    Returns (transaction_id, error). Uses the org's OWN chart: OHADA by real
    SYSCOHADA codes (5711 Cash / 7011 Sales of goods - local), IFRS by the
    IAS-1 template names. Never raises into the grading path - an inability
    to post is surfaced as practice_error, not a failed attempt.

    IDEMPOTENT: an already-posted transaction for this (user, question,
    organization) is returned unchanged instead of posting a second one, so a
    refresh, a retry, a double-click or a duplicate submission can never post the
    same business event twice (see `_existing_practice_post`). The returned id is
    identical on every call, so the client can treat it as a stable
    confirmation handle.
    """
    try:
        org = get_organization_for_user(db, user, org_id)
        # Correct org/workspace context: membership is enforced here by
        # `get_organization_for_user`, so a caller can never post the practice
        # entry into a workspace they do not belong to.
        existing = _existing_practice_post(db, user, question, org.id)
        if existing is not None:
            return existing, None
        accounts = db.query(Account).filter(Account.organization_id == org.id).all()
        if org.framework == "OHADA":
            cash = next((a for a in accounts if a.code == "5711"), None)
            sales = next((a for a in accounts if a.code == "7011"), None)
        else:
            cash = next(
                (a for a in accounts if a.name_en == "Cash and cash equivalents"), None
            )
            sales = next((a for a in accounts if a.name_en == "Sales revenue"), None)

        if cash is None or sales is None:
            return None, (
                "Practice posting needs the demo chart with Cash and Sales "
                "accounts — set up the demo workspace first"
            )

        # Fixed, balanced double entry (deterministic — no AI decides this):
        # Debit Cash (asset up), Credit Sales (revenue up). Posting enforces
        # debits == credits at the service layer, as everywhere else.
        amount = Decimal(str(amount))
        txn = transaction_service.create_draft_transaction(
            db=db,
            user=user,
            organization_id=org.id,
            description=_PRACTICE_DESCRIPTION,
            lines=[
                {
                    "account_id": cash.id,
                    "debit": amount,
                    "credit": Decimal("0"),
                    "narration": None,
                },
                {
                    "account_id": sales.id,
                    "debit": Decimal("0"),
                    "credit": amount,
                    "narration": None,
                },
            ],
        )
        posting_service.post_transaction(db, user, org.id, txn.id)
        db.commit()
        return txn.id, None
    except HTTPException as exc:
        db.rollback()
        return None, exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    except Exception:  # noqa: BLE001 — practice must never fail the grading path
        db.rollback()
        return None, "Could not post the practice transaction into the workspace"
def _refresh_progress(db: Session, user: User, lesson: Lesson) -> LessonProgress:
    """Recompute + persist the rolled-up progress row for (user, lesson).

    Roll-up semantics (Session 17 progress-fix): every count is DISTINCT
    questions, never raw attempt rows — retrying the same question must not
    inflate `questions_answered` (the reported "55 answered / 18 total"
    symptom) and must not flip a lesson to `completed` before every question
    was actually visited. For a question attempted more than once, only its
    LATEST attempt decides correctness: a corrected miss recovers best_score,
    a later wrong retry drops it again (deterministic, no AI).

    Review answers are part of the same stream (Session 18): `answer_review`
    records each graded review as an attempt on the SAME immutable question
    id, so "latest authoritative resolution" covers both lesson attempts and
    review resolutions with one rule. `total` comes from the deduplicated
    normal sequence, so counts can never exceed the denominator.
    """
    attempts = (
        db.query(Attempt)
        .filter(
            Attempt.user_id == user.id,
            Attempt.lesson_id == lesson.id,
        )
        .all()
    )
    # Bucket this lesson's attempts per question, keeping only each
    # question's LATEST attempt (attempt ids are insertion-ordered): retries
    # never inflate the counts, and correctness reflects current standing.
    latest: dict[int, Attempt] = {}
    for a in sorted(attempts, key=lambda x: x.id):
        latest[a.question_id] = a
    answered = len(latest)
    correct = sum(1 for a in latest.values() if a.is_correct)
    total = len(_normal_questions(lesson))
    best_score = round(correct / answered * 100) if answered else 0

    status_name = "not_started"
    completed_at = None
    if answered > 0:
        status_name = "in_progress"
    if total > 0 and answered >= total:
        status_name = "completed"
        completed_at = datetime.now(timezone.utc)

    row = (
        db.query(LessonProgress)
        .filter(
            LessonProgress.user_id == user.id,
            LessonProgress.lesson_id == lesson.id,
        )
        .first()
    )
    if row is None:
        row = LessonProgress(
            user_id=user.id, lesson_id=lesson.id, updated_at=datetime.now(timezone.utc)
        )
        db.add(row)
    row.status = status_name
    row.best_score = best_score
    row.questions_answered = answered
    row.questions_correct = correct
    row.practice_posted = any(a.practice_posted for a in attempts)
    row.completed_at = completed_at
    return row


def _localized(language: str, en: str | None, fr: str | None) -> str | None:
    """Pick the field for `language`, falling back to the other one if empty.

    The fallback exists only so a missing translation never leaves the learner
    with no feedback at all; it never mixes languages inside one message.
    """
    primary = fr if language == "fr" else en
    return primary or en or fr


def _remediation_target(
    question: Question, lesson: Lesson, language: str
) -> RemediationOut | None:
    """Optional "Review this concept" target for an INCORRECT answer (Part C1).

    Returns None (target omitted) unless the question points at a section that
    is verifiably part of THIS lesson — a stale, missing or cross-lesson pointer
    is dropped rather than guessed, so the UI never sends the learner to review
    something unrelated.
    """
    section_id = question.remediation_section_id
    if section_id is None:
        return None
    section = next((s for s in lesson.sections if s.id == section_id), None)
    if section is None:
        return None
    return RemediationOut(
        lesson_id=lesson.id,
        section_id=section.id,
        section_position=section.position,
        section_title=_localized(language, section.heading_en, section.heading_fr),
        action_label=feedback_copy.action_label(language),
    )


def _answer_feedback(
    question: Question, lesson: Lesson, is_correct: bool, lang: str | None
) -> AnswerFeedbackOut:
    """Build the learner-safe feedback object for one graded attempt (Part C1).

    - Correct: why the answer/reasoning is right + next-step encouragement.
    - Incorrect: the accounting concept behind the question + a plain-language
      correction of the reasoning + the optional remediation target.

    Never includes the correct option key, the correct option's stored text, the
    accepted short-answer text, or any grading detail — those stay in the
    pre-existing Part A fields that only exist after grading.
    """
    language = feedback_copy.resolve_language(lang)
    explanation = _localized(
        language, question.explanation_en, question.explanation_fr
    )
    if is_correct:
        return AnswerFeedbackOut(
            correct=True,
            explanation=explanation,
            encouragement=feedback_copy.encouragement(language),
        )
    return AnswerFeedbackOut(
        correct=False,
        explanation=explanation,
        correction=_localized(language, question.correction_en, question.correction_fr),
        remediation=_remediation_target(question, lesson, language),
    )


def _score_submission(
    question: Question, option_key: str | None, text: str | None
) -> tuple[bool, str | None, int | None]:
    """Straight-comparison scoring shared by lesson attempts AND review cards.

    No AI: the stored correct option / accepted short answers decide the
    outcome, exactly as since Part A. Raises 422 for a missing/unknown option
    key on an MCQ. Returns ``(is_correct, correct_option_key, selected_answer_id)``.
    """
    if question.kind == "mcq":
        if not option_key:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="option_key is required for multiple-choice questions",
            )
        chosen = next(
            (a for a in question.answers if a.option_key == option_key), None
        )
        if chosen is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unknown option_key for this question",
            )
        correct_option_key = next(
            (a.option_key for a in question.answers if a.is_correct), None
        )
        return bool(chosen.is_correct), correct_option_key, chosen.id
    submitted = _normalise(text or "")
    accepted = {
        _normalise(v)
        for v in [question.short_answer_en, question.short_answer_fr]
        if v
    }
    return bool(submitted and submitted in accepted), None, None


def submit_attempt(
    db: Session,
    user: User,
    lesson_id: int,
    question_id: int,
    option_key: str | None = None,
    text: str | None = None,
    organization_id: int | None = None,
    lang: str | None = None,
    confidence: str | None = None,
) -> AttemptOut:
    """Score one submitted answer (straight comparison) and record progress.

    Also triggers the Lesson 4 practice-connector posting when the answer is
    correct, the question opts in, and a demo workspace was provided.

    `lang` is the requested feedback language ('en' | 'fr'); when omitted the
    user's stored `language_preference` decides (see feedback.resolve_language).
    Scoring is unaffected by language: accepted short answers are always
    compared in BOTH languages, as before.

    Session 11 Part C2: the optional `confidence` self-assessment ('understood'
    | 'guessed') decides whether a spaced-review card is created — a wrong
    answer or a guessed correct answer (re)activates the user's review card for
    this question; a confident correct answer never creates one. Confidence
    NEVER changes the score.
    """
    ensure_default_lessons(db)
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found"
        )
    question = db.get(Question, question_id)
    if question is None or question.lesson_id != lesson.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    is_correct, correct_option_key, selected_answer_id = _score_submission(
        question, option_key, text
    )

    attempt = Attempt(
        user_id=user.id,
        lesson_id=lesson.id,
        question_id=question.id,
        selected_answer_id=selected_answer_id,
        submitted_text=text,
        is_correct=is_correct,
        organization_id=organization_id,
        confidence=confidence,
    )

    practice_transaction_id = None
    practice_error = None
    if is_correct and question.posts_demo_transaction and organization_id:
        amount = question.practice_amount if question.practice_amount is not None else 0
        practice_transaction_id, practice_error = _apply_practice_posting(
            db, user, question, organization_id, amount
        )
        # A repeat submission re-reports the SAME transaction rather than
        # creating a second one, so `practice_posted` stays a truthful "this
        # workspace has this transaction" flag instead of a per-click counter.
        attempt.practice_posted = practice_transaction_id is not None
        attempt.practice_transaction_id = practice_transaction_id

    db.add(attempt)
    # Part C2: (re)activate the user's spaced-review card for this question
    # according to the outcome + confidence. Same transaction — no review is
    # ever created for a question that failed to grade, and a card is never
    # created/modified by a confident correct answer.
    _apply_confidence_review(db, user, question, is_correct, confidence)
    # SessionLocal is created with autoflush=False, so the pending INSERT
    # would otherwise be invisible to _refresh_progress's Attempt query —
    # the rollup would report the user as one answer behind reality (and
    # persist that wrong count). Flush explicitly first.
    db.flush()
    progress = _refresh_progress(db, user, lesson)
    db.commit()

    return AttemptOut(
        question_id=question.id,
        lesson_id=lesson.id,
        is_correct=is_correct,
        correct_option_key=correct_option_key,
        correct_text=(
            None
            if question.kind == "mcq"
            else (question.short_answer_en or question.short_answer_fr)
        ),
        explanation_en=question.explanation_en,
        explanation_fr=question.explanation_fr,
        # Part C1: learner-safe feedback in the requested language. Only ever
        # returned here — the read endpoints do not carry it.
        feedback=_answer_feedback(question, lesson, is_correct, lang or user.language_preference),
        progress=LessonProgressOut(**_progress_dict(user, lesson, progress)),
        practice_posted=attempt.practice_posted,
        practice_transaction_id=attempt.practice_transaction_id,
        practice_error=practice_error,
        created_at=attempt.created_at,
    )


# --- Session 11 Part C2: confidence tracking + spaced review ------------------

#: Deterministic interval ladder, in days, indexed by the CURRENT stage after a
#: correct review answer: stage 0 -> 1 day, stage 1 -> 3 days, stage 2 -> 7 days
#: and stage 3+ -> 14 days (capped). A wrong review answer ignores this ladder
#: entirely: it resets the stage to 0 and makes the card due immediately.
_REVIEW_INTERVAL_DAYS = (1, 3, 7, 14)


def _stage_interval_days(stage: int) -> int:
    """Interval for the review card's CURRENT stage (caps at 14 days)."""
    return _REVIEW_INTERVAL_DAYS[min(max(stage, 0), len(_REVIEW_INTERVAL_DAYS) - 1)]


def _apply_confidence_review(
    db: Session,
    user: User,
    question: Question,
    is_correct: bool,
    confidence: str | None,
) -> None:
    """(Re)activate the user's spaced-review card for this question (Part C2).

    Rules (deterministic, per the C2 spec):
    - a WRONG lesson answer always creates/resets the card (due immediately);
    - a correct answer marked 'guessed' ("I got it, but I guessed") does the
      same;
    - a correct answer marked 'understood' ("I understand this") NEVER creates
      a new card — and deliberately does not touch an existing one either:
      cards only advance through their own review answers, so lesson confidence
      and review scheduling stay two independent, predictable mechanisms.

    The (user_id, question_id) unique constraint makes duplicate active cards
    impossible; an existing row is reset/reactivated in place instead.
    """
    if is_correct and confidence != "guessed":
        return  # 'understood' (or no confidence given): nothing to schedule
    outcome = "wrong" if not is_correct else "guessed"
    now = datetime.now(timezone.utc)
    item = (
        db.query(ReviewItem)
        .filter(
            ReviewItem.user_id == user.id,
            ReviewItem.question_id == question.id,
        )
        .first()
    )
    if item is None:
        item = ReviewItem(
            user_id=user.id,
            question_id=question.id,
            stage=0,
            due_at=now,
            is_active=True,
            last_outcome=outcome,
        )
        db.add(item)
        return
    item.stage = 0
    item.due_at = now
    item.is_active = True
    item.last_outcome = outcome


def _as_utc_aware(value: datetime) -> datetime:
    """Normalise a stored datetime to timezone-aware UTC.

    PostgreSQL's timestamptz returns aware datetimes; SQLite (tests) returns
    naive ones (it stores UTC strings without offset). Treating naive values as
    UTC keeps due-date comparisons correct on both engines.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _review_item_out(item: ReviewItem, now: datetime) -> ReviewItemOut:
    """Project one review card for its owner — question + options, NO key."""
    question = item.question
    lesson = question.lesson
    due_at = _as_utc_aware(item.due_at)
    return ReviewItemOut(
        id=item.id,
        question_id=question.id,
        lesson_id=lesson.id,
        lesson_title_en=lesson.title_en,
        lesson_title_fr=lesson.title_fr,
        question_en=question.question_en,
        question_fr=question.question_fr,
        kind=question.kind,
        answers=[
            QuestionAnswerOut(
                option_key=a.option_key, text_en=a.text_en, text_fr=a.text_fr
            )
            for a in _display_answers(question, lesson.slug)
        ],
        stage=item.stage,
        due_at=due_at,
        last_outcome=item.last_outcome,
        is_due=due_at <= now,
    )


def get_review_summary(db: Session, user: User) -> ReviewSummaryOut:
    """Counts for the signed-in user's review queue (authenticated, scoped)."""
    items = (
        db.query(ReviewItem)
        .filter(ReviewItem.user_id == user.id, ReviewItem.is_active.is_(True))
        .all()
    )
    now = datetime.now(timezone.utc)
    due = [i for i in items if _as_utc_aware(i.due_at) <= now]
    future = [i for i in items if _as_utc_aware(i.due_at) > now]
    return ReviewSummaryOut(
        total_active=len(items),
        due_now=len(due),
        scheduled=len(future),
        next_due_at=min((_as_utc_aware(i.due_at) for i in future), default=None),
    )


def list_reviews(
    db: Session, user: User, due_only: bool = False
) -> list[ReviewItemOut]:
    """The signed-in user's active review cards (optionally due ones only)."""
    items = (
        db.query(ReviewItem)
        .filter(ReviewItem.user_id == user.id, ReviewItem.is_active.is_(True))
        .order_by(ReviewItem.due_at.asc(), ReviewItem.id.asc())
        .all()
    )
    now = datetime.now(timezone.utc)
    out = [_review_item_out(item, now) for item in items]
    if due_only:
        out = [r for r in out if r.is_due]
    return out


def answer_review(
    db: Session,
    user: User,
    review_id: int,
    option_key: str | None = None,
    text: str | None = None,
    lang: str | None = None,
) -> ReviewAnswerOut:
    """Answer one of the user's OWN review cards (straight comparison).

    Scheduling (deterministic, UTC):
    - correct -> stage += 1 and due_at = now + interval(stage) where the
      interval ladder is 1 / 3 / 7 / 14 days (stage 3+ stays at 14);
    - incorrect -> stage reset to 0 and due_at = now (immediately).

    Session 18 hotfix — mastery linkage: each review answer IS recorded as an
    `attempts` row for the SAME immutable question id and that lesson's
    progress is rolled up from it (append-only history — nothing is ever
    deleted or rewritten), so correctly resolving a previously missed question
    updates current mastery (17/18 -> 18/18, 94% -> 100%). Completion and
    certificate eligibility still follow the UNCHANGED rule
    `status == "completed" AND best_score == 100` — this endpoint never
    bypasses it; it feeds it the learner's current resolved state.
    User scoping: the card is looked up by (id, user_id); anything else is a
    plain 404, so one user can neither read nor answer another user's card.
    The response NEVER carries the answer key (no correct option key/text, no
    accepted short-answer text) — only the Part C1 learner-safe feedback.
    """
    item = (
        db.query(ReviewItem)
        .filter(
            ReviewItem.id == review_id,
            ReviewItem.user_id == user.id,
            ReviewItem.is_active.is_(True),
        )
        .first()
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    question = item.question
    lesson = question.lesson

    is_correct, _correct_option_key, _selected_answer_id = _score_submission(
        question, option_key, text
    )

    # Session 18 hotfix: the review answer is this question's LATEST
    # authoritative resolution. Record it as an attempt row for the SAME
    # immutable question id (append-only — historical attempts are never
    # touched) so `_refresh_progress` folds it into current mastery exactly
    # like a lesson retry. No practice posting and no confidence-card logic
    # runs here — the C2 scheduling below is untouched.
    attempt = Attempt(
        user_id=user.id,
        lesson_id=lesson.id,
        question_id=question.id,
        selected_answer_id=_selected_answer_id,
        submitted_text=text,
        is_correct=is_correct,
    )
    db.add(attempt)

    now = datetime.now(timezone.utc)
    interval_days = None
    if is_correct:
        # The ladder is indexed by the stage the card WAS at: answering a
        # stage-0 card correctly schedules it 1 day ahead, stage-1 -> 3 days,
        # stage-2 -> 7 days, stage-3+ -> 14 days. The stage keeps counting up
        # but the interval caps at 14 (deterministic, no AI).
        interval_days = _stage_interval_days(item.stage)
        item.stage = item.stage + 1
        item.due_at = now + timedelta(days=interval_days)
        item.last_outcome = "review_correct"
    else:
        item.stage = 0
        item.due_at = now  # due again immediately
        item.last_outcome = "review_wrong"
    # autoflush=False: flush the pending attempt first so the roll-up query
    # sees it, then persist mastery in the SAME transaction as the schedule.
    db.flush()
    _refresh_progress(db, user, lesson)

    # Capture BEFORE commit: commit expires ORM attributes and a re-read would
    # return engine-dependent (naive on SQLite) datetimes.
    stage_after = item.stage
    due_after = item.due_at
    review_id_after = item.id
    db.commit()

    return ReviewAnswerOut(
        review_id=review_id_after,
        question_id=question.id,
        correct=is_correct,
        stage=stage_after,
        due_at=due_after,
        interval_days=interval_days,
        feedback=_answer_feedback(
            question, lesson, is_correct, lang or user.language_preference
        ),
    )
