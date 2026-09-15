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
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.learning.schemas import (
    AttemptCreate,
    AttemptOut,
    CourseCompletionOut,
    LessonDetailOut,
    LessonSummaryOut,
    ReviewAnswerCreate,
    ReviewAnswerOut,
    ReviewItemOut,
    ReviewSummaryOut,
)
from app.learning import service as learning_service
from app.schemas.certificate import CertificateOut, PublicCertificateOut
from app.services import certificate_service
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
    lang: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Score an answer by straight comparison and record the user's progress.

    A correct answer on the Lesson 4 practice question with an
    organization_id posts a real, balanced transaction into that workspace.

    Session 11 Part C1: the response also carries a learner-safe `feedback`
    object (explanation, optional correction/encouragement and an optional
    remediation target). `lang` ('en' | 'fr') chooses the feedback language;
    when it is omitted the signed-in user's stored language preference decides.
    Nothing about the answer key is served before submission.

    Session 11 Part C2: the optional `confidence` field ('understood' |
    'guessed') is a self-assessment — it never changes the score, it only
    decides whether the user's spaced-review card for this question is created
    or reset (wrong answer or guessed correct answer).
    """
    return learning_service.submit_attempt(
        db,
        current_user,
        lesson_id=payload.lesson_id,
        question_id=payload.question_id,
        option_key=payload.option_key,
        text=payload.text,
        organization_id=payload.organization_id,
        lang=lang,
        confidence=payload.confidence,
    )

# --- Part B1: authoritative completion + certificate -------------------------
@router.get("/reviews/summary", response_model=ReviewSummaryOut)
def get_review_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Counts for the signed-in user's spaced-review queue (Part C2).

    Authenticated and strictly user-scoped. Review data never changes lesson
    progress, completion or certificate eligibility.
    """
    return learning_service.get_review_summary(db, current_user)


@router.get("/reviews", response_model=list[ReviewItemOut])
def list_reviews(
    due_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """The signed-in user's active spaced-review cards (Part C2).

    `due_only=true` limits the list to cards whose `due_at` has passed.
    Cards carry the question and its selectable options — NEVER the answer
    key (no is_correct flag, no correct option key/text).
    """
    return learning_service.list_reviews(db, current_user, due_only=due_only)


@router.post("/reviews/{review_id}/answer", response_model=ReviewAnswerOut)
def answer_review(
    review_id: int,
    payload: ReviewAnswerCreate,
    lang: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Answer one of the user's OWN review cards (Part C2).

    Straight comparison, same as lesson scoring. Deterministic UTC schedule:
    correct advances the stage (1 / 3 / 7 / 14-day ladder), incorrect resets to
    stage 0 and is due again immediately. The response never exposes the
    answer key — only the learner-safe feedback object from Part C1.
    """
    return learning_service.answer_review(
        db,
        current_user,
        review_id=review_id,
        option_key=payload.option_key,
        text=payload.text,
        lang=lang,
    )


# --- Part B1: authoritative completion + certificate (unchanged) --------------
@router.get("/completion", response_model=CourseCompletionOut)
def get_completion(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Server-side completion status + the user's certificate, if issued."""
    learning_service.ensure_default_lessons(db)
    total, completed = certificate_service.course_completion_metrics(
        db, current_user
    )
    cert = certificate_service.get_certificate(db, current_user)
    is_completed = total > 0 and completed == total
    pct = round((completed / total) * 100) if total else 0
    status = "issued" if cert is not None else ("available" if is_completed else "locked")
    return CourseCompletionOut(
        completed=is_completed,
        certificate=cert,
        total_lessons=total,
        completed_lessons=completed,
        completion_percentage=pct,
        certificate_status=status,
    )


@router.post("/certificate", response_model=CertificateOut)
def issue_certificate(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Issue the certificate if (and only if) the course is complete.

    Idempotent: calling it again returns the SAME certificate row.
    """
    cert = certificate_service.issue_certificate_if_eligible(db, current_user)
    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Course not complete; certificate not eligible",
        )
    db.commit()
    return cert


# --- Part B3: public certificate verification ---------------------------------
@router.get("/certificates/verify/{credential_id}", response_model=PublicCertificateOut)
def verify_certificate(
    credential_id: str,
    db: Session = Depends(get_db),
):
    """Public read-only certificate verification (Session 11 Part B3).

    No authentication required. Accepts ONLY the public credential id —
    never the sequential integer PK. Returns a privacy-safe payload (no
    internal id, no user_id, no email, no workspace/transaction/answer data).
    Unknown ids return the standard 404 without revealing whether any
    related private user or workspace exists. Read-only: this is a GET that
    never mutates anything (no POST/PUT/DELETE/PATCH exists on this path).
    """
    cert = certificate_service.get_certificate_by_credential_id(db, credential_id)
    if cert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found",
        )
    return certificate_service.public_verification_payload(cert)
