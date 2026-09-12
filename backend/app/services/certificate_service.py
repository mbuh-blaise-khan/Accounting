"""Certificate service (Session 11 Part B1 + Part B3).

Authoritative server-side course completion + certificate issuance (B1),
plus privacy-safe public verification data (B3).

A lesson counts as PASSED only when the user has attempted every question
in that lesson and every attempt is correct (best_score == 100). The course
is COMPLETE when every lesson in the curriculum is passed. Issuance is
idempotent: the unique (user_id, course_slug) constraint means at most one
certificate exists per user per course.

Deterministic, no AI: completion is computed from stored rows only.
"""

import secrets

from sqlalchemy.orm import Session

from app.core.config import settings
from app.learning import service as learning_service
from app.models.certificate import Certificate
from app.models.learning import Lesson, LessonProgress
from app.models.user import User

# There is exactly one curriculum today; this slug identifies it.
COURSE_SLUG = "accounting-basics"
CERTIFICATE_WORDING = "Kinxta Docu Certificate of Completion"

# Public verification constants (Session 11 Part B3). The issuer name and
# course title are the ONLY authority/identity claims the product makes —
# no accreditation, regulator seal, professional body, CPD credits,
# signature, or license number exists anywhere in this codebase.
ISSUER_NAME = "Kinxta Docu"
COURSE_TITLE = "Accounting Basics"
STATUS_VALID = "valid"
STATUS_REVOKED = "revoked"


def _new_credential_id() -> str:
    """Unguessable ~256-bit public credential identifier (URL-safe)."""
    return f"kinxta-{secrets.token_urlsafe(32)}"


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
        credential_id=_new_credential_id(),
        status=STATUS_VALID,
        recipient_name=user.display_name or "",
    )
    db.add(cert)
    try:
        db.flush()
    except Exception:
        # A concurrent insert already created the certificate; return it.
        db.rollback()
        return get_certificate(db, user)
    return cert


def get_certificate_by_credential_id(
    db: Session, credential_id: str
) -> Certificate | None:
    """Look up a certificate by its PUBLIC credential id only (Part B3).

    The sequential integer PK is intentionally NEVER accepted here: a
    numeric-only input cannot be a real credential (ours always start with
    the 'kinxta-' prefix), so it fails closed to None without a DB hit.
    """
    if not credential_id or not credential_id.startswith("kinxta-"):
        return None
    return (
        db.query(Certificate)
        .filter(Certificate.credential_id == credential_id)
        .first()
    )


def public_verification_payload(cert: Certificate) -> dict:
    """Privacy-safe public verification data for one certificate (Part B3).

    Only credential metadata + the recipient display-name snapshot taken at
    issuance. NEVER: internal id, user_id, email, passwords, workspace data,
    transactions, journal lines, lesson answers, or org internals. Any stored
    status other than 'valid' renders as 'revoked' (fail closed — a revoked
    certificate must never look valid just because its id still exists).

    The public URL uses the same hash deep link the SPA actually serves
    (#/verify/<credential_id>): the app has no router dependency (view-switch
    architecture, .clinerules), so a plain path URL would 404 on refresh.
    """
    status = cert.status if cert.status == STATUS_VALID else STATUS_REVOKED
    origin = (settings.FRONTEND_ORIGIN or "").rstrip("/")
    return {
        "credential_id": cert.credential_id,
        "status": status,
        "issuer": ISSUER_NAME,
        "wording": cert.wording,
        "recipient_name": cert.recipient_name,
        "course_title": COURSE_TITLE,
        "course_slug": cert.course_slug,
        "issued_at": cert.issued_at,
        "completed_at": cert.issued_at,
        "verification_url": f"{origin}/#/verify/{cert.credential_id}"
        if origin
        else None,
    }
