"""Chart of accounts endpoints. All routes are protected and org-scoped."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.account import AccountCreate, AccountOut, AccountUpdate
from app.services import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
def list_accounts(
    organization_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the chart of accounts for an organization the user is a member of."""
    return account_service.list_accounts(db, current_user, organization_id)


@router.post("", response_model=AccountOut, status_code=201)
def create_account(
    payload: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a user-defined custom account (never a system default)."""
    return account_service.create_custom_account(
        db=db,
        user=current_user,
        organization_id=payload.organization_id,
        framework=payload.framework,
        code=payload.code,
        name_en=payload.name_en,
        name_fr=payload.name_fr,
        account_class=payload.account_class,
        normal_balance=payload.normal_balance,
        parent_account_id=payload.parent_account_id,
        description=payload.description,
        ohada_class_number=payload.ohada_class_number,
    )


@router.patch("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: int,
    payload: AccountUpdate,
    organization_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Edit plain-language names and/or toggle active for an org's account."""
    return account_service.update_account(
        db=db,
        user=current_user,
        org_id=organization_id,
        account_id=account_id,
        name_en=payload.name_en,
        name_fr=payload.name_fr,
        active=payload.active,
    )