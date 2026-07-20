"""
Pydantic settings — reads from environment variables (sourced from .env).
Centralises all configuration so services don't import os.environ directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # ── App metadata ────────────────────────────────────────────────────────
    app_name: str = "FastAPI Full Stack"
    app_debug: bool = False
    app_environment: str = "production"
    app_log_level: str = "info"
    app_secret_key: str = "change-me"
    app_cors_origins: str = "*"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_workers: int = 4

    # ── PostgreSQL ──────────────────────────────────────────────────────────
    postgres_server: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "fastapi_app"
    postgres_user: str = "app_user"
    postgres_password: str = ""
    database_url: str = (
        f"postgresql+asyncpg://{postgres_user}:{postgres_password}"
        f"@{postgres_server}:{postgres_port}/{postgres_db}"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_echo: bool = False

    # ── Redis ───────────────────────────────────────────────────────────────
    redis_server: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    redis_url: str = f"redis://:{redis_password}@{redis_server}:{redis_port}/{redis_db}"
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    redis_retry_on_timeout: bool = True
    redis_max_connections: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Singleton — lazily initialise and cache settings."""
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
