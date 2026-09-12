"""Certificate service (Session 11 Part B1).

Authoritative server-side course completion + certificate issuance.

A lesson counts as PASSED only when the user has attempted every question
in that lesson and every attempt is correct (best_score == 100). The course
is COMPLETE when every lesson in the curriculum is passed. Issuance is
idempotent: the unique (user_id, course_slug) constraint means at most one
certificate exists per user per course.

Deterministic, no AI: completion is computed from stored rows only.
"""

from sqlalchemy.orm import Session

from app.learning import service as learning_service
from app.models.certificate import Certificate
from app.models.learning import Lesson, LessonProgress
from app.models.user import User

# There is exactly one curriculum today; this slug identifies it.
COURSE_SLUG = "accounting-basics"
CERTIFICATE_WORDING = "Kinxta Docu Certificate of Completion"


def _lesson_passed(row: LessonProgress | None) -> bool:
    """Authoritative B1 rule: the lesson is completed AND fully correct."""
    return row is not None and row.status == "completed" and row.best_score == 100


def _all_lessons_passed(db: Session, user: User) -> bool:
    """True only when every lesson is completed AND fully correct (100%)."""
    lessons = db.query(Lesson).all()
    if not lessons:
        return False
    progress_rows = {
        p.lesson_id: p
        for p in db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id)
        .all()
    }
    return all(_lesson_passed(progress_rows.get(lesson.id)) for lesson in lessons)


def course_completion_metrics(db: Session, user: User) -> tuple[int, int]:
    """(total_lessons, completed_lessons) under the authoritative B1 rule."""
    lessons = db.query(Lesson).all()
    progress_rows = {
        p.lesson_id: p
        for p in db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id)
        .all()
    }
    total = len(lessons)
    completed = sum(
        1 for lesson in lessons if _lesson_passed(progress_rows.get(lesson.id))
    )
    return total, completed


def get_certificate(db: Session, user: User) -> Certificate | None:
    """Return the user's certificate for this course, if it exists."""
    return (
        db.query(Certificate)
        .filter(
            Certificate.user_id == user.id,
            Certificate.course_slug == COURSE_SLUG,
        )
        .first()
    )


def issue_certificate_if_eligible(db: Session, user: User) -> Certificate | None:
    """Create (or return the existing) certificate if the course is complete."""
    learning_service.ensure_default_lessons(db)
    if not _all_lessons_passed(db, user):
        return None
    existing = get_certificate(db, user)
    if existing is not None:
        return existing
    cert = Certificate(
        user_id=user.id,
        course_slug=COURSE_SLUG,
        wording=CERTIFICATE_WORDING,
    )
    db.add(cert)
    try:
        db.flush()
    except Exception:
        # A concurrent insert already created the certificate; return it.
        db.rollback()
        return get_certificate(db, user)
    return cert
