"""Organization (workspace) endpoints. All routes are protected."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.enums import FrameworkCode
from app.models.user import User
from app.schemas.organization import (
    IdentityOptionsOut,
    OrganizationCreate,
    OrganizationOut,
    OrganizationUpdate,
)
from app.services import organization_service

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/identity-options", response_model=IdentityOptionsOut)
def get_identity_options(
    framework: str = Query(..., description="OHADA or IFRS"),
    current_user: User = Depends(get_current_user),
):
    """Country + legal-form dropdown data for ONE framework. OHADA: only the
    17 member states and the AUSCGIE forms. IFRS: full international list."""
    if framework not in (FrameworkCode.OHADA.value, FrameworkCode.IFRS.value):
        return IdentityOptionsOut(countries=[], legal_forms=[])
    return IdentityOptionsOut(**organization_service.get_identity_options(framework))


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


@router.patch("/{org_id}", response_model=OrganizationOut)
def update_organization(
    org_id: int,
    payload: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the optional Business Profile (address, RCCM, tax ID, fiscal
    year start month). PATCH semantics: only provided fields change; all of
    them are optional so a workspace that isn't a registered business stays
    valid."""
    return organization_service.update_business_profile(
        db,
        current_user,
        org_id,
        **payload.model_dump(exclude_unset=True),
    )