"""Shared FastAPI dependencies, especially the protected-route guard.

get_current_user reads the JWT from either the `Authorization: Bearer <t>`
header or the httpOnly `access_token` cookie, decodes it, and loads the user.
Raises 401 when the token is missing or invalid.
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User


def _token_from_request(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[len("Bearer "):]
    return request.cookies.get(settings.COOKIE_NAME)


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = _token_from_request(request)
    if not token:
        raise credentials_exc

    payload = decode_access_token(token)
    if payload is None or payload.get("sub") is None:
        raise credentials_exc

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise credentials_exc

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exc
    return user
