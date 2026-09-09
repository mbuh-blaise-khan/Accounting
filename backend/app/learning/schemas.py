"""Pydantic schemas for the learning engine (Session 11 Part A)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


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
    position: int
    heading_en: Optional[str] = None
    heading_fr: Optional[str] = None
    body_en: str
    body_fr: str


class QuestionAnswerOut(BaseModel):
    """MCQ option — the is_correct flag is NEITHER stored nor sent here.

    Correct answers are learned only via the scoring endpoint (server-side
    straight comparison), so the client cannot just read them out of the
    lesson detail payload.
    """

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
    # The demo workspace to post into for the Lesson 4 practice connector
    # (only honored when the answer is correct AND the question posts).
    organization_id: Optional[int] = None


class AttemptOut(BaseModel):
    question_id: int
    lesson_id: int
    is_correct: bool
    # After grading (never revealed before): which option was right.
    correct_option_key: Optional[str] = None
    correct_text: Optional[str] = None  # short-answer accepted form
    explanation_en: Optional[str] = None
    explanation_fr: Optional[str] = None
    progress: LessonProgressOut
    # Lesson 4 practice connector:
    practice_posted: bool = False
    practice_transaction_id: Optional[int] = None
    practice_error: Optional[str] = None
    created_at: datetime