"""Framework registry endpoint (fed by the seeded data in framework_service)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.framework import FrameworkVersion
from app.models.user import User
from app.schemas.organization import FrameworkOut, FrameworkVersionOut
from app.services import framework_service

router = APIRouter(prefix="/frameworks", tags=["frameworks"])


@router.get("", response_model=list[FrameworkOut])
def list_frameworks(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    frameworks = framework_service.list_frameworks(db)
    result: list[FrameworkOut] = []
    for fw in frameworks:
        versions = (
            db.query(FrameworkVersion)
            .filter(FrameworkVersion.framework_id == fw.id)
            .order_by(FrameworkVersion.is_current.desc())
            .all()
        )
        result.append(
            FrameworkOut(
                id=fw.id,
                code=fw.code,
                name=fw.name,
                description_en=fw.description_en,
                description_fr=fw.description_fr,
                is_active=fw.is_active,
                versions=[FrameworkVersionOut.model_validate(v) for v in versions],
            )
        )
    return result