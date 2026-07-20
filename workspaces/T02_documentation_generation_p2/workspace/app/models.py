"""Pydantic models for Users, Products, and Orders API."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import re


# ──────────────────────────────────────────────
#  User Models
# ──────────────────────────────────────────────

class UserCreate(BaseModel):
    """Request model for creating a user."""
    name: str = Field(..., min_length=3, description="Full name, at least 3 characters")
    email: str = Field(..., description="Valid email address")
    age: int = Field(..., gt=0, lt=150, description="Age (1–149)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()


class UserUpdate(BaseModel):
    """Request model for updating a user. All fields optional."""
    name: Optional[str] = Field(None, min_length=3, description="Full name")
    email: Optional[str] = Field(None, description="Valid email address")
    age: Optional[int] = Field(None, gt=0, lt=150, description="Age (1–149)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()


class UserResponse(BaseModel):
    """Response model for a user."""
    id: int
    name: str
    email: str
    age: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
#  Product Models
# ──────────────────────────────────────────────

class ProductCreate(BaseModel):
    """Request model for creating a product."""
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: str = Field("", max_length=2000, description="Product description")
    price: Decimal = Field(..., gt=Decimal("0"), description="Price in EUR (positive)")
    stock: int = Field(0, ge=0, description="Available stock quantity")

    @field_validator("price")
    @classmethod
    def round_price(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))


class ProductUpdate(BaseModel):
    """Request model for updating a product. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    price: Optional[Decimal] = Field(None, gt=Decimal("0"), description="Price in EUR")
    stock: Optional[int] = Field(None, ge=0, description="Available stock")

    @field_validator("price")
    @classmethod
    def round_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            return v.quantize(Decimal("0.01"))
        return v


class ProductResponse(BaseModel):
    """Response model for a product."""
    id: int
    name: str
    description: str
    price: Decimal
    stock: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
#  Order Models
# ──────────────────────────────────────────────

class OrderItem(BaseModel):
    """An item within an order."""
    product_id: int = Field(..., description="ID of the product being ordered")
    quantity: int = Field(..., gt=0, description="Quantity (must be positive)")
    unit_price: Decimal = Field(..., gt=Decimal("0"), description="Price per unit at time of order")


class OrderCreate(BaseModel):
    """Request model for creating an order."""
    user_id: int = Field(..., description="ID of the user placing the order")
    items: List[OrderItem] = Field(..., min_length=1, description="Order items (at least 1)")
    shipping_address: str = Field(..., min_length=5, max_length=500, description="Shipping address")


class OrderResponse(BaseModel):
    """Response model for an order."""
    id: int
    user_id: int
    items: List[OrderItem]
    total: Decimal
    status: str
    shipping_address: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
