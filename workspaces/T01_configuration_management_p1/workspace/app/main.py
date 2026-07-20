"""FastAPI application entry point — used by the Dockerfile HEALTHCHECK & gunicorn."""

from fastapi import FastAPI

app = FastAPI(
    title="Python Web App",
    version="1.0.0",
    description="Production Python web app backed by PostgreSQL and Redis.",
)


@app.get("/health")
async def health():
    """Health check endpoint — returns 200 when the app is alive."""
    return {"status": "healthy"}
