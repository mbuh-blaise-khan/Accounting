"""User profile endpoints (no auth prefix, per spec: GET /me, PATCH /me)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.display_name is not None:
        current_user.display_name = payload.display_name.strip()
    if payload.language_preference is not None:
        current_user.language_preference = payload.language_preference
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user