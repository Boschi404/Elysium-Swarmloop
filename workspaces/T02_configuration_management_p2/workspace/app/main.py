"""
FastAPI application entry point.
Health-check endpoint, configuration management, and lifecycle hooks.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.settings import get_settings

log = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — startup / shutdown."""
    log.info("Starting %s …", settings.app_name)
    yield
    log.info("Shutting down %s …", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


# ─── Health check ───────────────────────────────────────────────────────────


@app.get("/health", tags=["system"])
async def health_check(request: Request) -> JSONResponse:
    """Liveness + readiness probe used by Docker health checks and Nginx."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.app_name,
        }
    )


@app.get("/", tags=["system"])
async def root() -> dict:
    """Root endpoint — returns API metadata."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
    }
