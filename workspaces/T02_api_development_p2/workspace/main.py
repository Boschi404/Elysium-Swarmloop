"""
Product Catalog API — FastAPI application.

Provides a complete CRUD interface for managing products
with filtering, pagination, and input validation.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid


app = FastAPI(title="Product Catalog", version="1.0.0")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ProductBase(BaseModel):
    """Shared product fields."""
    name: str = Field(..., min_length=1, description="Product name, must be non-empty")
    price: float = Field(..., gt=0, description="Product price, must be > 0")
    category: str = Field(..., min_length=1, description="Product category, must be non-empty")

    # --- explicit validators (belt and braces for non-empty) ---
    @field_validator("name")
    @classmethod
    def name_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("category")
    @classmethod
    def category_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("category must not be empty")
        return v.strip()

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be > 0")
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1)

    @field_validator("name")
    @classmethod
    def name_non_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("name must not be empty")
        return v.strip() if v else v

    @field_validator("category")
    @classmethod
    def category_non_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("category must not be empty")
        return v.strip() if v else v

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("price must be > 0")
        return v


class Product(ProductBase):
    """Full product schema including the auto-generated id."""
    id: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# In-memory data store
# ---------------------------------------------------------------------------

_products: dict[str, dict] = {}          # id -> product dict


def _next_id() -> str:
    """Return a short unique identifier."""
    return uuid.uuid4().hex[:12]


# ---------------------------------------------------------------------------
# Helper — build the response dict from stored data
# ---------------------------------------------------------------------------

def _product_dict(record: dict) -> dict:
    """Return a serialisable product dict from a store record."""
    return {
        "id": record["id"],
        "name": record["name"],
        "price": record["price"],
        "category": record["category"],
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/products", response_model=list[Product])
def list_products(
    category: Optional[str] = Query(None, description="Filter by exact category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> list[dict]:
    """Return a filtered, paginated list of products."""
    filtered = list(_products.values())

    if category is not None:
        filtered = [p for p in filtered if p["category"] == category]

    if min_price is not None:
        filtered = [p for p in filtered if p["price"] >= min_price]

    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    page_items = filtered[start:end]

    return [_product_dict(p) for p in page_items]


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> dict:
    """Return a single product by id."""
    record = _products.get(product_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return _product_dict(record)


@app.post("/products", response_model=Product, status_code=201)
def create_product(payload: ProductCreate) -> dict:
    """Create a new product."""
    pid = _next_id()
    record = {
        "id": pid,
        "name": payload.name,
        "price": payload.price,
        "category": payload.category,
    }
    _products[pid] = record
    return _product_dict(record)


@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: str, payload: ProductUpdate) -> dict:
    """Update an existing product (partial update allowed)."""
    record = _products.get(product_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.name is not None:
        record["name"] = payload.name
    if payload.price is not None:
        record["price"] = payload.price
    if payload.category is not None:
        record["category"] = payload.category

    _products[product_id] = record
    return _product_dict(record)


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str) -> None:
    """Delete a product by id."""
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Product not found")
    del _products[product_id]


# ---------------------------------------------------------------------------
# Health / root
# ---------------------------------------------------------------------------

@app.get("/")
def root() -> dict:
    return {"service": "Product Catalog API", "version": "1.0.0"}
