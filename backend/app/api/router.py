"""Aggregate API router. New endpoint modules are included here."""
from fastapi import APIRouter

from app.api.routes import auth, frameworks, health, organizations, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(organizations.router)
api_router.include_router(frameworks.router)
