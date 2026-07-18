"""
T02 — FastAPI Application entry point.

Exposes /health, /api/status, and a root endpoint.
Configured via environment variables (pydantic-settings).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic_settings import BaseSettings


# ── Configuration ─────────────────────────────────────
class AppSettings(BaseSettings):
    """Application settings loaded from environment / .env."""

    app_name: str = "T02 FastAPI Stack"
    app_version: str = "1.0.0"
    app_env: str = "production"
    log_level: str = "info"
    cors_origins: str = "*"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = AppSettings()


# ── Logging ───────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("Starting %s v%s [env=%s]", settings.app_name, settings.app_version, settings.app_env)
    yield
    logger.info("Shutting down %s", settings.app_name)


# ── Application ───────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


# ── Endpoints ─────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.app_env}


@app.get("/api/status")
async def api_status():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }
