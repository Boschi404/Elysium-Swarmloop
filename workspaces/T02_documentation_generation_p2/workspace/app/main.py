"""FastAPI API — Users, Products, and Orders (10 endpoints)."""
from fastapi import FastAPI, HTTPException, status
from typing import List

from app.models import (
    UserCreate, UserUpdate, UserResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    OrderCreate, OrderResponse,
)
from app.database import db

app = FastAPI(
    title="E-Commerce API",
    description="REST API for managing users, products, and orders with CRUD operations",
    version="1.0.0",
)


# ═══════════════════════════════════════════════
#  Users
# ═══════════════════════════════════════════════

@app.get(
    "/users",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users",
    description="Retrieve every registered user.",
)
async def list_users():
    """Return all users from the in-memory store."""
    return db.list_users()


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    description="Register a new user with name, email and age.",
)
async def create_user(user_data: UserCreate):
    """Create a new user."""
    return db.create_user(user_data.model_dump())


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve a single user by their unique identifier.",
)
async def get_user(user_id: int):
    """Return a user by ID."""
    user = db.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@app.put(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a user",
    description="Partially update a user's fields (name, email, age).",
)
async def update_user(user_id: int, user_data: UserUpdate):
    """Update an existing user."""
    payload = user_data.model_dump(exclude_unset=True)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update — supply at least one field",
        )
    updated = db.update_user(user_id, payload)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return updated


@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Remove a user by their ID.",
)
async def delete_user(user_id: int):
    """Delete a user by ID."""
    deleted = db.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return None


# ═══════════════════════════════════════════════
#  Products
# ═══════════════════════════════════════════════

@app.get(
    "/products",
    response_model=List[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="List all products",
    description="Retrieve the full product catalogue.",
)
async def list_products():
    """Return all products."""
    return db.list_products()


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
    description="Add a new product to the catalogue.",
)
async def create_product(product_data: ProductCreate):
    """Create a new product."""
    return db.create_product(product_data.model_dump())


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product by ID",
    description="Retrieve a single product by its unique identifier.",
)
async def get_product(product_id: int):
    """Return a product by ID."""
    product = db.get_product(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    return product


@app.put(
    "/products/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a product",
    description="Partially update a product's fields (name, description, price, stock).",
)
async def update_product(product_id: int, product_data: ProductUpdate):
    """Update an existing product."""
    payload = product_data.model_dump(exclude_unset=True)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update — supply at least one field",
        )
    updated = db.update_product(product_id, payload)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    return updated


# ═══════════════════════════════════════════════
#  Orders
# ═══════════════════════════════════════════════

@app.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an order",
    description="Place a new order with one or more items.",
)
async def create_order(order_data: OrderCreate):
    """Create a new order."""
    return db.create_order(order_data.model_dump())
