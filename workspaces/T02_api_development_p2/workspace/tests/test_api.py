"""Test suite for Product Catalog API — covers CRUD, validation, filtering, pagination."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from database import db


@pytest.fixture(autouse=True)
def clear_db():
    """Reset the in-memory database before each test."""
    db._products.clear()
    yield


transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_create_product():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/products", json={
            "name": "Laptop",
            "price": 999.99,
            "category": "Electronics",
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99
    assert data["category"] == "Electronics"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_products_empty():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/products")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["limit"] == 10


@pytest.mark.asyncio
async def test_get_product():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post("/products", json={
            "name": "Phone", "price": 599, "category": "Electronics",
        })
        pid = create.json()["id"]
        resp = await client.get(f"/products/{pid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Phone"


@pytest.mark.asyncio
async def test_get_product_not_found():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/products/nonexistent-id")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Product not found"


@pytest.mark.asyncio
async def test_update_product():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post("/products", json={
            "name": "Old Name", "price": 10, "category": "Stuff",
        })
        pid = create.json()["id"]
        resp = await client.put(f"/products/{pid}", json={
            "name": "New Name", "price": 20,
        })
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"
    assert resp.json()["price"] == 20
    assert resp.json()["category"] == "Stuff"  # unchanged


@pytest.mark.asyncio
async def test_update_product_not_found():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.put("/products/bad-id", json={"name": "X"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_product():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post("/products", json={
            "name": "Delete Me", "price": 5, "category": "Test",
        })
        pid = create.json()["id"]
        resp = await client.delete(f"/products/{pid}")
    assert resp.status_code == 204

    # Verify gone
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/products/{pid}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_not_found():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.delete("/products/bad-id")
    assert resp.status_code == 404


# ── Validation ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_product_empty_name():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/products", json={
            "name": "", "price": 10, "category": "Test",
        })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_product_empty_category():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/products", json={
            "name": "X", "price": 10, "category": "",
        })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_product_price_zero():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/products", json={
            "name": "X", "price": 0, "category": "Test",
        })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_product_negative_price():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/products", json={
            "name": "X", "price": -5, "category": "Test",
        })
    assert resp.status_code == 422


# ── Filtering ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_filter_by_category():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/products", json={"name": "A", "price": 1, "category": "Food"})
        await client.post("/products", json={"name": "B", "price": 2, "category": "Drink"})
        await client.post("/products", json={"name": "C", "price": 3, "category": "Food"})

        resp = await client.get("/products?category=Food")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert all(p["category"] == "Food" for p in data["items"])


@pytest.mark.asyncio
async def test_filter_by_price_range():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/products", json={"name": "A", "price": 10, "category": "X"})
        await client.post("/products", json={"name": "B", "price": 20, "category": "X"})
        await client.post("/products", json={"name": "C", "price": 30, "category": "X"})

        resp = await client.get("/products?min_price=15&max_price=25")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "B"


@pytest.mark.asyncio
async def test_pagination():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for i in range(1, 6):
            await client.post("/products", json={
                "name": f"Item {i}", "price": float(i), "category": "X",
            })

        resp = await client.get("/products?page=2&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 2
    # Items sorted by name: Item 1, Item 2, Item 3, Item 4, Item 5
    # Page 2 (limit=2): Item 3, Item 4
    assert data["items"][0]["name"] == "Item 3"
    assert data["items"][1]["name"] == "Item 4"


# ── Edge cases ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_only_optional_fields():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post("/products", json={
            "name": "Original", "price": 100, "category": "Cat",
        })
        pid = create.json()["id"]

        # Update only price
        resp = await client.put(f"/products/{pid}", json={"price": 50})
    assert resp.status_code == 200
    assert resp.json()["price"] == 50
    assert resp.json()["name"] == "Original"
    assert resp.json()["category"] == "Cat"


@pytest.mark.asyncio
async def test_update_invalid_price_still_rejected():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post("/products", json={
            "name": "X", "price": 10, "category": "Y",
        })
        pid = create.json()["id"]
        resp = await client.put(f"/products/{pid}", json={"price": -1})
    assert resp.status_code == 422
