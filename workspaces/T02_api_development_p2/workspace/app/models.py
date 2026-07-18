"""Pydantic models for the Product Catalog API."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    """Shared base fields for product operations."""

    name: str = Field(..., min_length=1, description="Product name (non-empty)")
    price: float = Field(..., gt=0, description="Product price (must be > 0)")
    category: str = Field(..., min_length=1, description="Product category (non-empty)")

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.strip()

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("category must not be blank")
        return v.strip()

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be greater than 0")
        return v


class ProductCreate(ProductBase):
    """Request model for creating a product."""
    pass


class ProductUpdate(ProductBase):
    """Request model for updating a product (full replacement per PUT semantics)."""
    pass


class ProductResponse(ProductBase):
    """Response model representing a single product."""

    id: int = Field(..., description="Unique product identifier")
    created_at: datetime = Field(..., description="Timestamp when the product was created")

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Response model for a paginated product list."""

    items: list[ProductResponse]
    total: int = Field(..., description="Total number of matching products")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, le=100, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(..., description="Error detail message")
