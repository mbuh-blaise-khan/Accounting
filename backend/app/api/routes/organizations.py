"""Organization (workspace) endpoints. All routes are protected."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationOut
from app.services import organization_service

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationOut, status_code=201)
def create_organization(
    payload: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return organization_service.create_organization(
        db=db,
        owner=current_user,
        name=payload.name,
        framework=payload.framework,
        currency=payload.currency,
        is_demo=payload.is_demo,
    )


@router.get("", response_model=list[OrganizationOut])
def list_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return organization_service.list_organizations_for_user(db, current_user)


@router.get("/{org_id}", response_model=OrganizationOut)
def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return organization_service.get_organization_for_user(db, current_user, org_id)