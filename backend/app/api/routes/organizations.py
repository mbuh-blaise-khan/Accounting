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
    WorkspaceDeleteIn,
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
    archived: bool = Query(
        False,
        description=(
            "false (default): ACTIVE workspaces only. true: ONLY the "
            "archived workspaces — the deliberate archived-retrieval path."
        ),
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List my workspaces. Default = active only; `archived=true` returns only
    archived ones (always membership-scoped, exactly like the active list)."""
    rows = organization_service.list_organizations_for_user(
        db, current_user, include_archived=archived
    )
    return [organization_service.serialize_organization(db, o) for o in rows]


@router.get("/{org_id}", response_model=OrganizationOut)
def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = organization_service.get_organization_for_user(db, current_user, org_id)
    return organization_service.serialize_organization(db, org)


@router.post("/{org_id}/archive", response_model=OrganizationOut)
def archive_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Archive a workspace (owner-only). Deletes nothing: the profile,
    accounts, drafts, posted transactions, reports and memberships stay; the
    workspace leaves the active list and becomes read-only at the service
    layer. Restore is always available."""
    org = organization_service.archive_organization(db, current_user, org_id)
    return organization_service.serialize_organization(db, org)


@router.post("/{org_id}/restore", response_model=OrganizationOut)
def restore_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Restore an archived workspace to the active list (owner-only)."""
    org = organization_service.restore_organization(db, current_user, org_id)
    return organization_service.serialize_organization(db, org)


@router.delete("/{org_id}", status_code=204)
def delete_organization(
    org_id: int,
    payload: WorkspaceDeleteIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permanently delete an ELIGIBLE workspace (owner-only).

    Server-side typed confirmation: `confirm_name` must exactly equal the
    current workspace name. Rejected with 409 when the workspace has ANY
    posted or reversed transaction — the only safe option then is archiving.
    """
    organization_service.delete_organization(
        db, current_user, org_id, payload.confirm_name
    )


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