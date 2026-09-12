"""Pydantic schemas for the learning engine (Session 11 Part A + Part B1)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.certificate import CertificateOut


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


class AttemptOut(BaseModel):
    question_id: int
    lesson_id: int
    is_correct: bool
    correct_option_key: Optional[str] = None
    correct_text: Optional[str] = None
    explanation_en: Optional[str] = None
    explanation_fr: Optional[str] = None
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
