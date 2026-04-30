"""
Configuration management using Pydantic Settings.

Pydantic Settings reads from environment variables AND from a .env file.
Every variable here is typed — if POSTGRES_PORT is set to "abc" instead
of a number, the app refuses to start. This is production-grade config.

Why not just use os.environ.get()?
Because that gives you raw strings with no validation, no defaults,
no documentation, and no autocompletion in your IDE. This is better.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"         # default matches docker-compose service name
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        """Async database URL for SQLAlchemy + asyncpg"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Sync database URL for Alembic migrations"""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"

    # ── Auth ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str                    # generate with: openssl rand -hex 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── AI ────────────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str

    # ── App ───────────────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """CORS allowed origins — tighter in production"""
        if self.ENVIRONMENT == "production":
            return ["https://yourdomain.com"]
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    # ── Pydantic Settings config ───────────────────────────────────────────────
    # env_file tells it to also read from .env
    # extra="ignore" means unknown env vars are silently ignored (not errors)
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True,
    )


# Singleton instance — import this everywhere
# `from app.core.config import settings`
settings = Settings()
