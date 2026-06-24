"""Application configuration via Pydantic Settings.

All values can be overridden through environment variables or a local `.env`
file (see `.env.example`). Keep this lightweight so the API boots on low-end
machines without optional heavy dependencies.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        # Disable JSON decoding at the env-source level so CORS_ORIGINS can be
        # supplied as a plain comma-separated string (parsed by the validator
        # below). Without this, pydantic-settings tries json.loads first and
        # raises on a non-JSON value. CORS_ORIGINS is the only complex field.
        enable_decoding=False,
    )

    # --- App ---
    APP_NAME: str = "Miori Core"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # --- Server ---
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./miori.db"

    # --- CORS ---
    # Comma-separated list in env, e.g. "http://localhost:3000,http://localhost:1420".
    # Default to explicit localhost dev origins (NOT "*") so allow_credentials
    # stays safe; override via CORS_ORIGINS for other setups.
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

    # --- Feature flags ---
    # When True, remote dashboard / device sync endpoints are active.
    # TODO(Mark-XLVI): wire real remote session transport when enabled.
    REMOTE_ENABLED: bool = True

    # Lite mode keeps optional heavy deps (vector stores, embeddings, real model
    # providers) lazy/disabled so Miori stays usable on low-end machines.
    LITE_MODE: bool = True

    # --- Paths ---
    # Location of shared prompt profiles in the monorepo. Persona service degrades
    # gracefully if this path is missing.
    PROMPTS_DIR: str = "../../packages/prompts"
    UPLOAD_DIR: str = "./data/uploads"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor."""
    return Settings()


settings = get_settings()
