"""Pydantic models for the FastAPI application."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


# ─── User Models ─────────────────────────────────────────────────

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the user")
    email: str = Field(..., description="Email address of the user")
    role: str = Field(default="customer", description="User role (admin, customer)")


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="Timestamp when the user was created")

    class Config:
        from_attributes = True


# ─── Product Models ───────────────────────────────────────────────

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: str = Field(default="", max_length=2000, description="Detailed product description")
    price: float = Field(..., gt=0, description="Product price in EUR")
    stock: int = Field(default=0, ge=0, description="Available stock quantity")
    category: str = Field(default="general", description="Product category")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, max_length=2000, description="Detailed product description")
    price: Optional[float] = Field(None, gt=0, description="Product price in EUR")
    stock: Optional[int] = Field(None, ge=0, description="Available stock quantity")
    category: Optional[str] = Field(None, description="Product category")


class Product(ProductBase):
    id: int = Field(..., description="Unique product identifier")
    created_at: datetime = Field(..., description="Timestamp when the product was created")

    class Config:
        from_attributes = True


# ─── Order Models ─────────────────────────────────────────────────

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0, description="ID of the product being ordered")
    quantity: int = Field(..., gt=0, description="Quantity of the product")


class OrderCreate(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the user placing the order")
    items: list[OrderItem] = Field(..., min_length=1, description="List of items in the order")


class OrderUpdate(BaseModel):
    status: OrderStatus = Field(..., description="New status for the order")


class OrderItemResponse(BaseModel):
    product_id: int = Field(..., description="ID of the product")
    product_name: str = Field(..., description="Name of the product at time of order")
    quantity: int = Field(..., description="Quantity ordered")
    unit_price: float = Field(..., description="Price per unit at time of order")


class Order(BaseModel):
    id: int = Field(..., description="Unique order identifier")
    user_id: int = Field(..., description="ID of the user who placed the order")
    items: list[OrderItemResponse] = Field(..., description="Items in the order")
    total: float = Field(..., description="Total order amount in EUR")
    status: OrderStatus = Field(..., description="Current order status")
    created_at: datetime = Field(..., description="Timestamp when the order was created")
    updated_at: datetime = Field(..., description="Timestamp of last status update")

    class Config:
        from_attributes = True


# ─── Error Response ───────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable error message")
    error_code: str = Field(..., description="Machine-readable error code")
