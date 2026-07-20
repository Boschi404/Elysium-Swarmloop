"""Product Catalog API — FastAPI application with full CRUD + filtering + pagination."""

from fastapi import FastAPI, HTTPException, Query
from models import Product, ProductCreate, ProductUpdate
from database import db

app = FastAPI(
    title="Product Catalog API",
    version="1.0.0",
    description="A simple product catalog with filtering and pagination.",
)


@app.get("/products", response_model=dict)
def list_products(
    category: str = Query(None, description="Filter by category (case-insensitive)"),
    min_price: float = Query(None, gt=0, description="Minimum price filter"),
    max_price: float = Query(None, gt=0, description="Maximum price filter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """List products with optional filtering and pagination."""
    items, total = db.list_products(
        category=category,
        min_price=min_price,
        max_price=max_price,
        page=page,
        limit=limit,
    )
    return {
        "items": [p.model_dump() for p in items],
        "total": total,
        "page": page,
        "limit": limit,
    }


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    """Get a single product by ID."""
    product = db.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=Product, status_code=201)
def create_product(data: ProductCreate):
    """Create a new product."""
    return db.create_product(data)


@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: str, data: ProductUpdate):
    """Update an existing product."""
    product = db.update_product(product_id, data)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str):
    """Delete a product by ID."""
    deleted = db.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return None
