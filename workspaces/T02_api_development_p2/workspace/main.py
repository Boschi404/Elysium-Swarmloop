"""
Product Catalog API — FastAPI with Pydantic validation, filtering, and pagination.

Endpoints:
    GET    /products       — list products (filterable + paginated)
    GET    /products/{id}  — get single product
    POST   /products       — create a product
    PUT    /products/{id}  — update a product
    DELETE /products/{id}  — delete a product
"""

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Product Catalog API")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    name: str = Field(..., min_length=1, description="Product name (non-empty)")
    price: float = Field(..., gt=0, description="Product price (> 0)")
    category: str = Field(..., min_length=1, description="Product category (non-empty)")


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    name: Optional[str] = Field(None, min_length=1, description="Product name (non-empty)")
    price: Optional[float] = Field(None, gt=0, description="Product price (> 0)")
    category: Optional[str] = Field(None, min_length=1, description="Product category (non-empty)")


class Product(ProductCreate):
    """Schema for a product returned in API responses."""
    id: int


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

_products: list[dict] = []
_next_id: int = 1


def _next_product_id() -> int:
    global _next_id
    pid = _next_id
    _next_id += 1
    return pid


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/products", response_model=list[Product])
def list_products(
    category: Optional[str] = Query(None, min_length=1),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
) -> list[Product]:
    """List products with optional filtering and pagination."""
    result = _products

    if category is not None:
        result = [p for p in result if p["category"] == category]
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    start = (page - 1) * limit
    end = start + limit
    return result[start:end]


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int) -> Product:
    """Get a single product by ID."""
    for p in _products:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products", response_model=Product, status_code=201)
def create_product(body: ProductCreate) -> Product:
    """Create a new product."""
    product = body.model_dump()
    product["id"] = _next_product_id()
    _products.append(product)
    return product


@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, body: ProductUpdate) -> Product:
    """Update an existing product (partial update)."""
    for p in _products:
        if p["id"] == product_id:
            update_data = body.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=400,
                    detail="No fields to update",
                )
            p.update(update_data)
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int) -> None:
    """Delete a product by ID."""
    for i, p in enumerate(_products):
        if p["id"] == product_id:
            _products.pop(i)
            return
    raise HTTPException(status_code=404, detail="Product not found")
