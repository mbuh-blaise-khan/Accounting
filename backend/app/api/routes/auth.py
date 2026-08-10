"""Authentication endpoints.

The JWT is delivered as an httpOnly cookie (not readable by frontend JS) to
reduce the risk of token theft via script-injection/XSS bugs. SameSite=Lax
covers localhost dev; set COOKIE_SECURE=True behind HTTPS in production.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.COOKIE_SECURE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(key=settings.COOKIE_NAME, path="/")


def _get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.strip().lower()).first()


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email is required",
        )
    if _get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        display_name=payload.display_name.strip(),
        language_preference=payload.language_preference,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _set_auth_cookie(response, create_access_token(str(user.id)))
    return user


@router.post("/login", response_model=UserOut)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = _get_user_by_email(db, payload.email)
    # Generic message to avoid leaking whether the email exists.
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    _set_auth_cookie(response, create_access_token(str(user.id)))
    return user


@router.post("/logout")
def logout(response: Response):
    _clear_auth_cookie(response)
    return {"message": "Logged out"}
