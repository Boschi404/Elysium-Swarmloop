"""Product Catalog API — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router as products_router

app = FastAPI(
    title="Product Catalog API",
    description="A RESTful API for managing a product catalog with filtering and pagination.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
