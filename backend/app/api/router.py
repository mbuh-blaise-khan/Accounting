"""Aggregate API router. New endpoint modules are included here."""
from fastapi import APIRouter

from app.api.routes import (
    accounts,
    auth,
    frameworks,
    health,
    journal,
    organizations,
    transactions,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(organizations.router)
api_router.include_router(frameworks.router)
api_router.include_router(accounts.router)
api_router.include_router(transactions.router)
api_router.include_router(journal.router)
