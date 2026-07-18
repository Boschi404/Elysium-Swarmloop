"""Product Catalog API — benchmark-compatible entry point.

Re-exports everything from the structured app package so that
`from main import app` and `import main` both work for tests.
"""

from app.main import app
from app.models import (
    ErrorResponse,
    ProductBase,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.database import db, ProductDatabase

__all__ = [
    "app",
    "db",
    "ProductDatabase",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductListResponse",
    "ErrorResponse",
]
