"""Tests for the Product Catalog API.

Covers all CRUD endpoints, filtering, pagination, and validation.
Uses TestClient for synchronous testing against the FastAPI app.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.database import db
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the in-memory database before each test."""
    # Access the internal store to clear it
    with db._lock:
        db._products.clear()
        db._next_id = 1
    yield


client = TestClient(app)


# ── Helpers ──────────────────────────────────────────────────────────────

def seed_products(count: int = 5, category: str = "electronics") -> list[int]:
    """Insert *count* products into the DB and return their ids."""
    ids = []
    for i in range(count):
        resp = client.post(
            "/products",
            json={"name": f"Product {i}", "price": 10.0 + i, "category": category},
        )
        assert resp.status_code == status.HTTP_201_CREATED, resp.text
        ids.append(resp.json()["id"])
    return ids


# ── POST /products ──────────────────────────────────────────────────────

class TestCreateProduct:
    def test_create_valid_product(self):
        resp = client.post(
            "/products",
            json={"name": "Laptop", "price": 999.99, "category": "electronics"},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["name"] == "Laptop"
        assert data["price"] == 999.99
        assert data["category"] == "electronics"
        assert isinstance(data["id"], int)
        assert "created_at" in data

    def test_create_empty_name_returns_422(self):
        resp = client.post(
            "/products",
            json={"name": "", "price": 10.0, "category": "test"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_blank_name_returns_422(self):
        resp = client.post(
            "/products",
            json={"name": "   ", "price": 10.0, "category": "test"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_empty_category_returns_422(self):
        resp = client.post(
            "/products",
            json={"name": "Test", "price": 10.0, "category": ""},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_blank_category_returns_422(self):
        resp = client.post(
            "/products",
            json={"name": "Test", "price": 10.0, "category": "   "},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_zero_price_returns_422(self):
        resp = client.post(
            "/products",
            json={"name": "Test", "price": 0, "category": "test"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_negative_price_returns_422(self):
        resp = client.post(
            "/products",
            json={"name": "Test", "price": -5.0, "category": "test"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_missing_fields_returns_422(self):
        resp = client.post("/products", json={})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ── GET /products ───────────────────────────────────────────────────────

class TestListProducts:
    def test_list_empty(self):
        resp = client.get("/products")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["pages"] == 0

    def test_list_all_products(self):
        seed_products(3)
        resp = client.get("/products")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1
        assert data["limit"] == 10

    def test_list_pagination(self):
        seed_products(25)
        # Page 1: limit=10
        resp = client.get("/products?page=1&limit=10")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["total"] == 25
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["pages"] == 3

        # Page 3: last page should have 5 items
        resp = client.get("/products?page=3&limit=10")
        data = resp.json()
        assert len(data["items"]) == 5
        assert data["page"] == 3

    def test_list_filter_by_category(self):
        seed_products(3, category="electronics")
        seed_products(2, category="books")
        resp = client.get("/products?category=electronics")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["total"] == 3
        assert all(p["category"] == "electronics" for p in data["items"])

    def test_list_filter_by_min_price(self):
        seed_products(5)  # prices: 10, 11, 12, 13, 14
        resp = client.get("/products?min_price=12")
        data = resp.json()
        assert data["total"] == 3  # 12, 13, 14

    def test_list_filter_by_max_price(self):
        seed_products(5)  # prices: 10, 11, 12, 13, 14
        resp = client.get("/products?max_price=11")
        data = resp.json()
        assert data["total"] == 2  # 10, 11

    def test_list_filter_by_price_range(self):
        seed_products(5)
        resp = client.get("/products?min_price=11&max_price=13")
        data = resp.json()
        assert data["total"] == 3  # 11, 12, 13

    def test_list_filter_no_match(self):
        seed_products(3)
        resp = client.get("/products?category=nonexistent")
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_pagination_edge_page_too_high(self):
        seed_products(5)
        resp = client.get("/products?page=100&limit=10")
        data = resp.json()
        assert data["total"] == 5
        assert data["items"] == []
        assert data["pages"] == 1

    @pytest.mark.parametrize("limit", [1, 50, 100])
    def test_list_valid_limit_values(self, limit):
        seed_products(60)
        resp = client.get(f"/products?limit={limit}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) == min(limit, 60)

    def test_list_limit_exceeds_max_returns_422(self):
        resp = client.get("/products?limit=101")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_page_zero_returns_422(self):
        resp = client.get("/products?page=0")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ── GET /products/{id} ──────────────────────────────────────────────────

class TestGetProduct:
    def test_get_existing_product(self):
        ids = seed_products(1)
        resp = client.get(f"/products/{ids[0]}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["id"] == ids[0]
        assert data["name"] == "Product 0"

    def test_get_nonexistent_product_returns_404(self):
        resp = client.get("/products/99999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in resp.json()["detail"].lower()


# ── PUT /products/{id} ──────────────────────────────────────────────────

class TestUpdateProduct:
    def test_update_existing_product(self):
        ids = seed_products(1)
        resp = client.put(
            f"/products/{ids[0]}",
            json={"name": "Updated", "price": 49.99, "category": "updated-cat"},
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["name"] == "Updated"
        assert data["price"] == 49.99
        assert data["category"] == "updated-cat"
        assert data["id"] == ids[0]

    def test_update_nonexistent_returns_404(self):
        resp = client.put(
            "/products/99999",
            json={"name": "Nope", "price": 1.0, "category": "test"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_update_invalid_price_returns_422(self):
        ids = seed_products(1)
        resp = client.put(
            f"/products/{ids[0]}",
            json={"name": "Bad", "price": 0, "category": "test"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_empty_name_returns_422(self):
        ids = seed_products(1)
        resp = client.put(
            f"/products/{ids[0]}",
            json={"name": "", "price": 10.0, "category": "test"},
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ── DELETE /products/{id} ───────────────────────────────────────────────

class TestDeleteProduct:
    def test_delete_existing_product(self):
        ids = seed_products(1)
        resp = client.delete(f"/products/{ids[0]}")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        resp = client.get(f"/products/{ids[0]}")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_returns_404(self):
        resp = client.delete("/products/99999")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ── Health ──────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_endpoint(self):
        resp = client.get("/health")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["status"] == "ok"


# ── Integration: Full workflow ──────────────────────────────────────────

class TestWorkflow:
    def test_full_crud_workflow(self):
        # Create
        resp = client.post(
            "/products",
            json={"name": "Widget", "price": 25.0, "category": "gadgets"},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        pid = resp.json()["id"]

        # List
        resp = client.get("/products")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["total"] == 1

        # Get single
        resp = client.get(f"/products/{pid}")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["name"] == "Widget"

        # Update
        resp = client.put(
            f"/products/{pid}",
            json={"name": "Widget Pro", "price": 35.0, "category": "gadgets"},
        )
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["price"] == 35.0

        # Delete
        resp = client.delete(f"/products/{pid}")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        # Verify gone
        resp = client.get("/products")
        assert resp.json()["total"] == 0
