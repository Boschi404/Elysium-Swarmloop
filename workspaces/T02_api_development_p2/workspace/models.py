"""Pydantic models for the Product Catalog API."""

from pydantic import BaseModel, Field
from typing import Optional
import uuid


class ProductBase(BaseModel):
    """Shared product fields."""
    name: str = Field(..., min_length=1, description="Product name (must be non-empty)")
    price: float = Field(..., gt=0, description="Product price (must be > 0)")
    category: str = Field(..., min_length=1, description="Product category (must be non-empty)")


class ProductCreate(ProductBase):
    """Model for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Model for updating an existing product. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, description="Product name (must be non-empty if provided)")
    price: Optional[float] = Field(None, gt=0, description="Product price (must be > 0 if provided)")
    category: Optional[str] = Field(None, min_length=1, description="Product category (must be non-empty if provided)")


class Product(ProductBase):
    """Full product model returned by the API."""
    id: str = Field(..., description="Unique product identifier")

    model_config = {"from_attributes": True}


def generate_id() -> str:
    """Generate a unique product ID."""
    return str(uuid.uuid4())
