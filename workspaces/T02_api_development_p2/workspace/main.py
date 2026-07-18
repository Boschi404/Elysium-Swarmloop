"""
Product Catalog API — FastAPI implementation with filtering, pagination, and validation.

Endpoints:
    GET    /products        — List products with optional filtering and pagination
    GET    /products/{id}   — Get a single product by ID
    POST   /products        — Create a new product
    PUT    /products/{id}   — Update an existing product
    DELETE /products/{id}   — Delete a product
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, model_validator

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ProductBase(BaseModel):
    """Shared product fields."""

    name: str = Field(..., min_length=1, description="Product name (required, non-empty)")
    price: float = Field(..., gt=0, description="Product price (must be > 0)")
    category: str = Field(..., min_length=1, description="Product category (required, non-empty)")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    @model_validator(mode="after")
    def validate_name_non_empty(self) -> "ProductCreate":
        if not self.name.strip():
            raise ValueError("name must not be empty or whitespace-only")
        return self

    @model_validator(mode="after")
    def validate_category_non_empty(self) -> "ProductCreate":
        if not self.category.strip():
            raise ValueError("category must not be empty or whitespace-only")
        return self


class ProductUpdate(BaseModel):
    """Schema for updating an existing product. All fields are optional but at least one must be set."""

    name: Optional[str] = Field(None, min_length=1, description="Product name")
    price: Optional[float] = Field(None, gt=0, description="Product price (must be > 0)")
    category: Optional[str] = Field(None, min_length=1, description="Product category")

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ProductUpdate":
        if self.name is None and self.price is None and self.category is None:
            raise ValueError("at least one field must be provided for update")
        return self

    @model_validator(mode="after")
    def validate_name_non_empty(self) -> "ProductUpdate":
        if self.name is not None and not self.name.strip():
            raise ValueError("name must not be empty or whitespace-only")
        return self

    @model_validator(mode="after")
    def validate_category_non_empty(self) -> "ProductUpdate":
        if self.category is not None and not self.category.strip():
            raise ValueError("category must not be empty or whitespace-only")
        return self


class ProductResponse(ProductBase):
    """Schema returned to the client after a successful create / update / get."""

    id: str = Field(..., description="Unique product identifier")

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    """Wrapper for paginated list responses."""

    items: list[ProductResponse]
    total: int
    page: int
    limit: int
    pages: int

# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_store: dict[str, dict] = {}  # id -> product data


def _next_id() -> str:
    return uuid.uuid4().hex[:12]

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(title="Product Catalog API", version="1.0.0")


# -- GET /products ----------------------------------------------------------

@app.get("/products", response_model=PaginatedResponse)
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
) -> PaginatedResponse:
    """List products with optional filtering by category and price range, plus pagination."""
    items = list(_store.values())

    # -- filtering --
    if category:
        items = [p for p in items if p["category"].lower() == category.lower()]
    if min_price is not None:
        items = [p for p in items if p["price"] >= min_price]
    if max_price is not None:
        items = [p for p in items if p["price"] <= max_price]

    # -- pagination --
    total = len(items)
    pages = max(1, (total + limit - 1) // limit) if total else 1
    start = (page - 1) * limit
    end = start + limit
    page_items = items[start:end]

    return PaginatedResponse(
        items=[ProductResponse(**p) for p in page_items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


# -- GET /products/{id} -----------------------------------------------------

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str) -> ProductResponse:
    """Get a single product by its unique identifier."""
    product = _store.get(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{product_id}' not found",
        )
    return ProductResponse(**product)


# -- POST /products ---------------------------------------------------------

@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate) -> ProductResponse:
    """Create a new product."""
    product_id = _next_id()
    record = payload.model_dump()
    record["id"] = product_id
    _store[product_id] = record
    return ProductResponse(**record)


# -- PUT /products/{id} -----------------------------------------------------

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, payload: ProductUpdate) -> ProductResponse:
    """Update an existing product. Only supplied fields are updated."""
    if product_id not in _store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{product_id}' not found",
        )

    record = _store[product_id]
    update_data = payload.model_dump(exclude_unset=True)
    record.update(update_data)
    _store[product_id] = record

    return ProductResponse(**record)


# -- DELETE /products/{id} --------------------------------------------------

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str) -> None:
    """Delete a product by its unique identifier."""
    if product_id not in _store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{product_id}' not found",
        )
    del _store[product_id]
    return None
