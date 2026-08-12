"""Application settings loaded from backend/.env (falls back to dev defaults).

Uses pydantic-settings. The env file path is resolved relative to this file so
it works whether we run from the repo root or from backend/.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[0]=core, [1]=app, [2]=backend
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = (
        "postgresql+psycopg2://uap:uap_dev_password@localhost:5432/uap_dev"
    )
    SECRET_KEY: str = "dev-secret-change-me"
    ENV: str = "development"
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # Auth / JWT (Session 3)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    COOKIE_NAME: str = "access_token"
    # Set True only behind HTTPS (production). Kept False for local dev.
    COOKIE_SECURE: bool = False
    # bcrypt cost factor. Lower = faster hashing (useful for local dev/tests).
    # Raise to >=12 before any production deployment.
    BCRYPT_ROUNDS: int = 4


settings = Settings()
