"""Learning engine models (Session 11 Part A).

Six simple tables — no AI generation, straight stored-content + straight
comparison scoring, exactly per the MVP blueprint:
  - lessons         (the 7 seeded plain-language lessons, EN+FR)
  - lesson_sections (ordered content blocks inside a lesson)
  - questions       (2-3 per lesson: 'mcq' | 'short_answer', stored answers)
  - answers         (MCQ options; en/fr text + is_correct flag)
  - attempts        (one row per submitted answer, per user)
  - progress        (rolled-up per-user progress per lesson)

Correct-answer content is NEVER exposed by the read endpoints (they only
serve options without the is_correct flag) — scoring happens server-side
via straight comparison on POST /learning/attempts.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    # Ordered per the ACCA FIA-style progression (also this app's own
    # Sessions 4-10 build order): context -> equation -> debits/credits ->
    # journal -> ledger -> trial balance -> financial statements.
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title_en: Mapped[str] = mapped_column(String(200), nullable=False)
    title_fr: Mapped[str] = mapped_column(String(200), nullable=False)
    summary_en: Mapped[str] = mapped_column(Text, nullable=False)
    summary_fr: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sections: Mapped[list["LessonSection"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="LessonSection.position",
    )
    questions: Mapped[list["Question"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="Question.position",
    )


class LessonSection(Base):
    __tablename__ = "lesson_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    heading_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    heading_fr: Mapped[str | None] = mapped_column(String(200), nullable=True)
    body_en: Mapped[str] = mapped_column(Text, nullable=False)
    body_fr: Mapped[str] = mapped_column(Text, nullable=False)

    lesson: Mapped["Lesson"] = relationship(back_populates="sections")
class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    question_en: Mapped[str] = mapped_column(Text, nullable=False)
    question_fr: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # 'mcq' | 'short_answer'
    explanation_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_fr: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Session 11 Part C1 -- post-submission corrections and remediation.
    # correction_en/fr: plain-language correction shown after a wrong answer.
    #   States what is correct without exposing the correct option key/text.
    # remediation_section_id: optional pointer to a section of THIS question's
    #   lesson for "Review this concept". Never points at another lesson.
    correction_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    correction_fr: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation_section_id: Mapped[int | None] = mapped_column(
        ForeignKey("lesson_sections.id", ondelete="SET NULL"), nullable=True
    )
    # Session 11 Part C1 — post-submission learner feedback. Like the
    # explanations above, these are NEVER served by the read endpoints; they are
    # returned only by the scoring endpoint (POST /learning/attempts).
    # - correction_en/fr: authored, plain-language correction of the reasoning.
    #   It states WHAT is right WITHOUT ever echoing the correct option key, the
    #   option's stored text, or the short-answer accepted text (that would leak
    #   the answer key).
    # - remediation_section_id: OPTIONAL pointer to the single most relevant
    #   section of THIS question's own lesson ("Review this concept"). Nullable
    #   by design — omitted rather than guessed when no clearly-relevant section
    #   exists. ON DELETE SET NULL so section content edits can never cascade
    #   into question loss.
    #   The lesson is NOT duplicated here: `lesson_id` above is authoritative,
    #   and the service verifies the section belongs to that same lesson.
    correction_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    correction_fr: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation_section_id: Mapped[int | None] = mapped_column(
        ForeignKey("lesson_sections.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Short-answer questions store accepted answers (straight comparison).
    short_answer_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    short_answer_fr: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Lesson 4 practice-connector flag: a CORRECT answer on this question posts
    # a real, balanced double-entry transaction into the user's demo workspace
    # (Learn Mode -> Practice Mode). Informational; never auto-forced.
    posts_demo_transaction: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    practice_amount: Mapped[float | None] = mapped_column(Numeric(16, 2), nullable=True)

    lesson: Mapped["Lesson"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Answer.position",
    )
    # Session 11 Part C1 — the optional "Review this concept" target. Read-only
    # from the scoring endpoint, which additionally verifies the section belongs
    # to the same lesson (lesson_id + lesson_sections.lesson_id) before exposing
    # anything to the client.
    remediation_section: Mapped["LessonSection | None"] = relationship(
        foreign_keys=[remediation_section_id]
    )
    # Session 11 Part C2 — spaced-review cards that point at this question
    # (at most one per user, enforced by review_items' unique constraint).
    review_items: Mapped[list["ReviewItem"]] = relationship(back_populates="question")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    option_key: Mapped[str] = mapped_column(String(4), nullable=False)  # 'A', 'B', ...
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    text_en: Mapped[str] = mapped_column(String(300), nullable=False)
    text_fr: Mapped[str] = mapped_column(String(300), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    question: Mapped["Question"] = relationship(back_populates="answers")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id"), nullable=False, index=True
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"), nullable=False, index=True
    )
    selected_answer_id: Mapped[int | None] = mapped_column(
        ForeignKey("answers.id"), nullable=True
    )
    submitted_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Session 11 Part C2 — optional learner self-assessment sent WITH the
    # answer: 'understood' ("I understand this") or 'guessed' ("I got it, but
    # I guessed"). NULL when the client does not send it (older clients).
    # It NEVER affects scoring — only whether a spaced-review item is created.
    confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )
    practice_posted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    practice_transaction_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class LessonProgress(Base):
    __tablename__ = "progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="not_started", nullable=False
    )  # 'not_started' | 'in_progress' | 'completed'
    best_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_answered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    practice_posted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ReviewItem(Base):
    """One spaced-review card per (user, question) — Session 11 Part C2.

    Deterministic spaced repetition, no AI: the stage index alone decides the
    next due date (see learning/service.py `_stage_interval_days`):

        correct review answer:  stage 0 -> 1 day, 1 -> 3 days, 2 -> 7 days,
                                3+ -> 14 days (interval caps at 14)
        incorrect review answer: reset to stage 0, due immediately

    - The UNIQUE (user_id, question_id) constraint makes duplicate active
      reviews for the same user/question IMPOSSIBLE at the database level;
      an existing row is updated (reset/reactivated) instead of duplicated.
    - `is_active` retires a card only through a confident lesson answer path
      reserved for later UX; wrong/guessed answers always (re)activate it.
    - All timestamps are timezone-aware UTC (same convention as the rest of
      the learning engine).
    - Review rows NEVER influence lesson progress, completion or certificate
      eligibility: they are answered on their own endpoints and create no
      `attempts` rows.
    """

    __tablename__ = "review_items"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_review_user_question"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # 0-based stage into the interval ladder; reset to 0 on any wrong answer.
    stage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # 'wrong' | 'guessed' (lesson-created) | 'review_correct' | 'review_wrong'
    last_outcome: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    question: Mapped["Question"] = relationship(back_populates="review_items")