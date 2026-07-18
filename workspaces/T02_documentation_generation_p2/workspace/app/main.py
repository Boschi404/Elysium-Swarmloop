"""
FastAPI Application — E-Commerce API
======================================
A demonstration FastAPI application with 10 REST endpoints covering
users, products, and orders CRUD operations.

Endpoints:
  - Users:  GET /users, POST /users          (2)
  - Products: GET /products, POST /products, PUT /products/{id}, DELETE /products/{id}  (4)
  - Orders: GET /orders, POST /orders, PUT /orders/{id}, DELETE /orders/{id}  (4)
Total: 10 endpoints
"""

from fastapi import FastAPI, HTTPException, status
from app.models import (
    User, UserCreate, Product, ProductCreate, ProductUpdate,
    Order, OrderCreate, OrderUpdate, ErrorResponse
)
from app.database import db

app = FastAPI(
    title="E-Commerce API",
    description="A sample FastAPI application for managing users, products, and orders.",
    version="1.0.0",
)


# ═══════════════════════════════════════════════════════════════
#  USERS
# ═══════════════════════════════════════════════════════════════

@app.get(
    "/users",
    response_model=list[User],
    summary="List all users",
    description="Retrieve a list of all registered users.",
    responses={
        200: {"description": "A list of users"},
    },
    tags=["Users"],
)
def list_users():
    """GET /users — Return all users."""
    return db.get_users()


@app.post(
    "/users",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Register a new user with name, email and role.",
    responses={
        201: {"description": "User created successfully", "model": User},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    tags=["Users"],
)
def create_user(data: UserCreate):
    """POST /users — Create a new user."""
    return db.create_user(data)


# ═══════════════════════════════════════════════════════════════
#  PRODUCTS
# ═══════════════════════════════════════════════════════════════

@app.get(
    "/products",
    response_model=list[Product],
    summary="List all products",
    description="Retrieve a list of all available products.",
    responses={
        200: {"description": "A list of products"},
    },
    tags=["Products"],
)
def list_products():
    """GET /products — Return all products."""
    return db.get_products()


@app.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Add a new product to the catalog.",
    responses={
        201: {"description": "Product created successfully", "model": Product},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    tags=["Products"],
)
def create_product(data: ProductCreate):
    """POST /products — Create a new product."""
    return db.create_product(data)


@app.put(
    "/products/{product_id}",
    response_model=Product,
    summary="Update a product",
    description="Update an existing product by its ID. Supports partial updates.",
    responses={
        200: {"description": "Product updated successfully", "model": Product},
        404: {"description": "Product not found", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    tags=["Products"],
)
def update_product(product_id: int, data: ProductUpdate):
    """PUT /products/{id} — Update a product by ID."""
    updated = db.update_product(product_id, data)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found"
        )
    return updated


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    description="Remove a product from the catalog by its ID.",
    responses={
        204: {"description": "Product deleted successfully"},
        404: {"description": "Product not found", "model": ErrorResponse},
    },
    tags=["Products"],
)
def delete_product(product_id: int):
    """DELETE /products/{id} — Delete a product by ID."""
    deleted = db.delete_product(product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id={product_id} not found"
        )


# ═══════════════════════════════════════════════════════════════
#  ORDERS
# ═══════════════════════════════════════════════════════════════

@app.get(
    "/orders",
    response_model=list[Order],
    summary="List all orders",
    description="Retrieve a list of all orders placed.",
    responses={
        200: {"description": "A list of orders"},
    },
    tags=["Orders"],
)
def list_orders():
    """GET /orders — Return all orders."""
    return db.get_orders()


@app.post(
    "/orders",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Place a new order",
    description="Create a new order with items for a specific user.",
    responses={
        201: {"description": "Order created successfully", "model": Order},
        404: {"description": "User or product not found", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    tags=["Orders"],
)
def create_order(data: OrderCreate):
    """POST /orders — Place a new order."""
    # Verify user exists
    user = db.get_user(data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={data.user_id} not found"
        )
    return db.create_order(data)


@app.put(
    "/orders/{order_id}",
    response_model=Order,
    summary="Update order status",
    description="Update the status of an existing order (e.g. shipped, delivered, cancelled).",
    responses={
        200: {"description": "Order updated successfully", "model": Order},
        404: {"description": "Order not found", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
    },
    tags=["Orders"],
)
def update_order(order_id: int, data: OrderUpdate):
    """PUT /orders/{id} — Update order status."""
    updated = db.update_order(order_id, data)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id={order_id} not found"
        )
    return updated


@app.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an order",
    description="Remove an order from the system by its ID.",
    responses={
        204: {"description": "Order deleted successfully"},
        404: {"description": "Order not found", "model": ErrorResponse},
    },
    tags=["Orders"],
)
def delete_order(order_id: int):
    """DELETE /orders/{id} — Delete an order by ID."""
    deleted = db.delete_order(order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id={order_id} not found"
        )
