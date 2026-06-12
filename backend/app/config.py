"""
Application configuration using Pydantic BaseSettings.
Loads from .env file and environment variables.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the KSP Crime Intelligence Platform."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    app_name: str = "KSP Crime Intelligence Platform"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # ── Security ─────────────────────────────────────────────────────────
    secret_key: str = "change-this-to-a-random-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # ── PostgreSQL ───────────────────────────────────────────────────────
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "ksp_user"
    postgres_password: str = "ksp_secure_pass_2025"
    postgres_db: str = "ksp_crime_intel"
    database_url: str = "sqlite+aiosqlite:///./ksp_crime.db"

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "")

    # ── Neo4j ────────────────────────────────────────────────────────────
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "ksp_neo4j_2025"

    # ── Redis ────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── ChromaDB ─────────────────────────────────────────────────────────
    chromadb_host: str = "localhost"
    chromadb_port: int = 8100

    # ── Gemini AI ────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.3
    gemini_max_tokens: int = 4096

    # ── Celery ───────────────────────────────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
