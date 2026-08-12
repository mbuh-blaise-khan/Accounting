"""Framework service: idempotent seeding + queries for the framework registry.

Only metadata lives here; the chart of accounts for a framework is seeded in
Session 5 (illustrative/demo data, clearly labeled).
"""
from sqlalchemy.orm import Session

from app.models.enums import FrameworkCode
from app.models.framework import Framework, FrameworkVersion


def ensure_default_frameworks(db: Session) -> list[Framework]:
    """Insert (or update) the default frameworks and one current version each.

    Idempotent: safe to call on every startup / seed run / test setup.
    """
    defaults = [
        {
            "code": FrameworkCode.OHADA,
            "name": "OHADA",
            "description_en": (
                "The accounting framework used in most French-speaking African "
                "countries that belong to the OHADA zone."
            ),
            "description_fr": (
                "Le référentiel comptable des pays membres de l'OHADA, "
                "principalement en Afrique francophone."
            ),
            "version": "SYSCOHADA (revision 2017)",
        },
        {
            "code": FrameworkCode.IFRS,
            "name": "IFRS",
            "description_en": (
                "International Financial Reporting Standards, used by companies "
                "around the world."
            ),
            "description_fr": (
                "Normes internationales d'information financière, utilisées par "
                "les entreprises dans le monde entier."
            ),
            "version": "IFRS consolidated (2023)",
        },
    ]

    created = []
    for item in defaults:
        framework = db.query(Framework).filter(Framework.code == item["code"]).first()
        if framework is None:
            framework = Framework(
                code=item["code"],
                name=item["name"],
                description_en=item["description_en"],
                description_fr=item["description_fr"],
                is_active=True,
            )
            db.add(framework)
            created.append(framework)
        else:
            framework.name = item["name"]
            framework.description_en = item["description_en"]
            framework.description_fr = item["description_fr"]
            framework.is_active = True

        db.flush()  # assign framework.id
        version = (
            db.query(FrameworkVersion)
            .filter(FrameworkVersion.framework_id == framework.id)
            .first()
        )
        if version is None:
            db.add(
                FrameworkVersion(
                    framework_id=framework.id,
                    version_label=item["version"],
                    is_current=True,
                    description=item["description_en"],
                )
            )

    db.commit()
    return created


def list_frameworks(db: Session) -> list[Framework]:
    return db.query(Framework).filter(Framework.is_active.is_(True)).all()


def get_framework_by_code(db: Session, code: str) -> Framework | None:
    return db.query(Framework).filter(Framework.code == code).first()