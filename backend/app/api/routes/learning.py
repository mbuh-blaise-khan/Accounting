"""Learning engine endpoints (Session 11 Part A).

GET  /learning/lessons        — curriculum list + per-user progress
GET  /learning/lessons/{id}   — full lesson content (served per-request)
POST /learning/attempts       — score an answer, record progress (and, for
                                the Lesson 4 practice connector, post a real
                                transaction into the user's demo workspace)

All routes require authentication. Content lives in the DATABASE and is
served per-request — never bundled as static/downloadable files (content
deterrent requirement).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.learning.schemas import AttemptCreate, AttemptOut, LessonDetailOut, LessonSummaryOut
from app.learning import service as learning_service
from app.models.user import User

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/lessons", response_model=list[LessonSummaryOut])
def list_lessons(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """All 7 curriculum lessons in order, each with the user's progress."""
    return learning_service.list_lessons(db, current_user)


@router.get("/lessons/{lesson_id}", response_model=LessonDetailOut)
def get_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full lesson content (sections + questions, correct answers hidden)."""
    return learning_service.get_lesson(db, current_user, lesson_id)


@router.post("/attempts", response_model=AttemptOut)
def submit_attempt(
    payload: AttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Score an answer by straight comparison and record the user's progress.

    A correct answer on the Lesson 4 practice question with an
    organization_id posts a real, balanced transaction into that workspace.
    """
    return learning_service.submit_attempt(
        db,
        current_user,
        lesson_id=payload.lesson_id,
        question_id=payload.question_id,
        option_key=payload.option_key,
        text=payload.text,
        organization_id=payload.organization_id,
    )