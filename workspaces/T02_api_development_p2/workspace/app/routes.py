"""Product catalog API routes."""

from math import ceil
from typing import Optional, Union

from fastapi import APIRouter, HTTPException, Query, status

from app.database import db
from app.models import (
    ErrorResponse,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products",
    description="Retrieve a paginated list of products with optional filtering by category and price range.",
)
def list_products(
    category: Optional[str] = Query(None, description="Filter by exact category name"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
) -> ProductListResponse:
    items, total = db.list(
        category=category,
        min_price=min_price,
        max_price=max_price,
        page=page,
        limit=limit,
    )
    pages = ceil(total / limit) if total > 0 else 0
    return ProductListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    responses={404: {"model": ErrorResponse, "description": "Product not found"}},
    summary="Get product by ID",
    description="Retrieve a single product by its unique identifier.",
)
def get_product(product_id: int) -> ProductResponse:
    product = db.get_by_id(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    return product


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
    summary="Create a product",
    description="Create a new product. Name and category must be non-empty, price must be greater than 0.",
)
def create_product(data: ProductCreate) -> ProductResponse:
    return db.create(data)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Product not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
    summary="Update a product",
    description="Fully replace a product's data (PUT semantics). All fields are required.",
)
def update_product(product_id: int, data: ProductUpdate) -> ProductResponse:
    product = db.update(product_id, data)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Product not found"},
    },
    summary="Delete a product",
    description="Delete a product by its unique identifier.",
)
def delete_product(product_id: int) -> None:
    deleted = db.delete(product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    return None
