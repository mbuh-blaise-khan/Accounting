"""Pydantic schemas for the learning engine (Session 11 Part A + Part B1)."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.certificate import CertificateOut, PublicCertificateOut


class LessonProgressOut(BaseModel):
    """Per-user progress for one lesson (rolled up server-side)."""

    status: str = "not_started"  # 'not_started' | 'in_progress' | 'completed'
    best_score: int = 0  # 0-100 over the questions answered so far
    questions_total: int = 0
    questions_answered: int = 0
    questions_correct: int = 0
    practice_posted: bool = False


class LessonSummaryOut(BaseModel):
    """One row of the /learning/lessons list (no section/question content)."""

    id: int
    slug: str
    position: int
    title_en: str
    title_fr: str
    summary_en: str
    summary_fr: str
    progress: LessonProgressOut


class LessonSectionOut(BaseModel):
    """One content block of a lesson.

    `id` is the stable server-side section id (used by the Part C1
    remediation action to focus the right section). It is an identifier only —
    no answer material rides along with it.
    """

    id: Optional[int] = None
    position: int
    heading_en: Optional[str] = None
    heading_fr: Optional[str] = None
    body_en: str
    body_fr: str


class QuestionAnswerOut(BaseModel):
    """MCQ option - the is_correct flag is NEITHER stored nor sent here."""

    option_key: str
    text_en: str
    text_fr: str


class QuestionOut(BaseModel):
    id: int
    position: int
    question_en: str
    question_fr: str
    kind: str  # 'mcq' | 'short_answer'
    answers: list[QuestionAnswerOut] = []
    posts_demo_transaction: bool = False


class LessonDetailOut(BaseModel):
    id: int
    slug: str
    position: int
    title_en: str
    title_fr: str
    summary_en: str
    summary_fr: str
    sections: list[LessonSectionOut] = []
    questions: list[QuestionOut] = []
    progress: LessonProgressOut


class AttemptCreate(BaseModel):
    lesson_id: int
    question_id: int
    option_key: Optional[str] = Field(default=None, max_length=4)
    text: Optional[str] = Field(default=None, max_length=500)
    organization_id: Optional[int] = None
    # Session 11 Part C2 — optional learner self-assessment sent WITH the
    # answer ('understood' = "I understand this", 'guessed' = "I got it, but
    # I guessed"). Pydantic's Literal rejects anything else with a 422. It
    # NEVER changes scoring — only whether a spaced-review item is created.
    confidence: Optional[Literal["understood", "guessed"]] = None


class RemediationOut(BaseModel):
    """Optional "Review this concept" target for an INCORRECT answer (Part C1).

    Always a section of the SAME lesson as the question being graded — the
    service resolves it from that lesson's own sections, so it can never point
    at another lesson. Omitted when the question has no clearly-relevant
    section. Contains no answer material: just where to re-read and what to
    call the action.
    """

    lesson_id: int
    section_id: int
    section_position: int
    section_title: Optional[str] = None  # localized heading, if the section has one
    action_label: str  # localized, e.g. "Review this concept"


class AnswerFeedbackOut(BaseModel):
    """Learner-safe feedback for one submitted answer (Session 11 Part C1).

    Returned ONLY from POST /learning/attempts (after submission). Read
    endpoints (lesson list/detail) never carry it, and it never contains the
    correct option key, the correct option's stored text, the accepted
    short-answer text, or any grading implementation detail.

    - `correct`: mirrors the scored outcome (`AttemptOut.is_correct` is the
      project's existing name for the same fact; this field keeps the feedback
      object self-describing for clients that read only it).
    - `explanation`: why the answer is right (correct) / the accounting concept
      behind the question (incorrect), in the requested language only.
    - `encouragement`: optional next-step encouragement.
    - `correction`: plain-language correction of the reasoning (incorrect only).
    - `remediation`: optional pointer to the lesson section to review.
    """

    correct: Optional[bool] = None
    explanation: Optional[str] = None
    encouragement: Optional[str] = None
    correction: Optional[str] = None
    remediation: Optional[RemediationOut] = None


class AttemptOut(BaseModel):
    question_id: int
    lesson_id: int
    is_correct: bool
    correct_option_key: Optional[str] = None
    correct_text: Optional[str] = None
    explanation_en: Optional[str] = None
    explanation_fr: Optional[str] = None
    feedback: Optional[AnswerFeedbackOut] = None
    progress: LessonProgressOut
    practice_posted: bool = False
    practice_transaction_id: Optional[int] = None
    practice_error: Optional[str] = None
    created_at: datetime


class CourseCompletionOut(BaseModel):
    """Server-side authoritative course completion status (Part B1 + B2).

    `certificate_status` is server-computed so the UI never has to guess:
    'locked' (course not complete) | 'available' (complete, not yet issued)
    | 'issued' (certificate exists).
    """

    completed: bool
    certificate: Optional[CertificateOut] = None
    total_lessons: int = 0
    completed_lessons: int = 0
    completion_percentage: int = 0  # 0-100, rounded
    certificate_status: str = "locked"  # 'locked' | 'available' | 'issued'


# --- Session 11 Part C2: confidence tracking + spaced review ------------------

class ReviewSummaryOut(BaseModel):
    """Counts for the signed-in user's review queue (authenticated, scoped).

    `due_now` counts active cards whose `due_at` is in the past or now;
    `scheduled` counts active cards not yet due. Review data never changes
    lesson progress, completion or certificate eligibility.
    """

    total_active: int = 0
    due_now: int = 0
    scheduled: int = 0
    next_due_at: Optional[datetime] = None  # earliest future due date, UTC


class ReviewItemOut(BaseModel):
    """One spaced-review card for the signed-in user.

    Carries the QUESTION and its selectable options (exactly like the lesson
    detail payload) so the review UI can be built later WITHOUT any answer
    material: no `is_correct` flag, no correct option key/text and no accepted
    short-answer text ever rides on a review response.
    """

    id: int
    question_id: int
    lesson_id: int
    lesson_title_en: str
    lesson_title_fr: str
    question_en: str
    question_fr: str
    kind: str  # 'mcq' | 'short_answer'
    answers: list[QuestionAnswerOut] = []  # options only — never the key
    stage: int
    due_at: datetime  # timezone-aware UTC
    last_outcome: Optional[str] = None
    is_due: bool


class ReviewAnswerCreate(BaseModel):
    """One answer to a review card (straight comparison, same as lessons)."""

    option_key: Optional[str] = Field(default=None, max_length=4)
    text: Optional[str] = Field(default=None, max_length=500)


class ReviewAnswerOut(BaseModel):
    """Result of answering a review card.

    DELIBERATELY NARROWER than the lesson attempt response: it has NO
    `correct_option_key`, NO `correct_text` and NO top-level `explanation_en/fr`
    — the review endpoints must never expose the answer key. The learner-safe
    `feedback` object (explanation / correction / optional remediation target,
    all prose authored in the seed) is reused from Part C1.
    """

    review_id: int
    question_id: int
    correct: bool
    stage: int
    due_at: datetime  # next due date, timezone-aware UTC
    interval_days: Optional[int] = None  # days until due_at (None when reset)
    feedback: AnswerFeedbackOut
