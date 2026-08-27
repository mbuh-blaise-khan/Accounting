"""Kinxta Docu — FastAPI application entry point.

Run from the backend/ directory:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title="Kinxta Docu API",
    description="Backend for the bilingual (EN/FR) accounting learning & practice platform.",
    version="0.1.0",
)

# Allow the Vite dev server to call this API in development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root() -> dict:
    return {"message": "Kinxta Docu API", "docs": "/docs"}
