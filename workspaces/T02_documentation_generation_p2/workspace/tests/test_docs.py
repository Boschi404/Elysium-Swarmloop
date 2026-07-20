"""Tests for API Documentation generation."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    db.reset()
    yield


# ── Verify the OpenAPI spec ─────────────────

def test_openapi_spec_exists():
    """The app must have an OpenAPI spec."""
    spec = app.openapi()
    assert spec is not None
    assert "paths" in spec
    assert "components" in spec


def test_openapi_spec_title():
    spec = app.openapi()
    assert spec["info"]["title"] == "E-Commerce API"


def test_openapi_spec_version():
    spec = app.openapi()
    assert spec["info"]["version"] == "1.0.0"


def test_all_10_endpoints_in_openapi():
    spec = app.openapi()
    paths = spec["paths"]
    # We have 5 URL patterns but 10 method×path combos
    ops = 0
    for path, methods in paths.items():
        ops += len(methods)
    assert ops == 10, f"Expected 10 operations, got {ops}"


def test_endpoints_users():
    spec = app.openapi()
    assert "/users" in spec["paths"]
    assert "get" in spec["paths"]["/users"]
    assert "post" in spec["paths"]["/users"]


def test_endpoints_users_id():
    spec = app.openapi()
    assert "/users/{user_id}" in spec["paths"]
    assert "get" in spec["paths"]["/users/{user_id}"]
    assert "put" in spec["paths"]["/users/{user_id}"]
    assert "delete" in spec["paths"]["/users/{user_id}"]


def test_endpoints_products():
    spec = app.openapi()
    assert "/products" in spec["paths"]
    assert "get" in spec["paths"]["/products"]
    assert "post" in spec["paths"]["/products"]


def test_endpoints_products_id():
    spec = app.openapi()
    assert "/products/{product_id}" in spec["paths"]
    assert "get" in spec["paths"]["/products/{product_id}"]
    assert "put" in spec["paths"]["/products/{product_id}"]


def test_endpoint_orders():
    spec = app.openapi()
    assert "/orders" in spec["paths"]
    assert "post" in spec["paths"]["/orders"]


def test_all_summaries_present():
    spec = app.openapi()
    for path, methods in spec["paths"].items():
        for method, op in methods.items():
            assert op.get("summary"), f"Missing summary on {method.upper()} {path}"


def test_all_descriptions_present():
    spec = app.openapi()
    for path, methods in spec["paths"].items():
        for method, op in methods.items():
            assert op.get("description"), f"Missing description on {method.upper()} {path}"


# ── Verify the generated markdown doc ────────

def test_doc_file_exists():
    import os
    doc_path = "API_DOCUMENTATION.md"
    assert os.path.exists(doc_path), f"Documentation file {doc_path} not found"
    size = os.path.getsize(doc_path)
    assert size > 1000, f"Documentation file too small: {size} bytes"


def test_doc_contains_all_endpoints():
    with open("API_DOCUMENTATION.md") as f:
        content = f.read()
    expected = [
        "GET /users",
        "POST /users",
        "GET /users/{user_id}",
        "PUT /users/{user_id}",
        "DELETE /users/{user_id}",
        "GET /products",
        "POST /products",
        "GET /products/{product_id}",
        "PUT /products/{product_id}",
        "POST /orders",
    ]
    for ep in expected:
        assert ep in content, f"Endpoint '{ep}' not found in documentation"


def test_doc_contains_schemas():
    with open("API_DOCUMENTATION.md") as f:
        content = f.read()
    schemas = ["UserCreate", "UserUpdate", "UserResponse",
               "ProductCreate", "ProductUpdate", "ProductResponse",
               "OrderCreate", "OrderResponse", "OrderItem"]
    for s in schemas:
        assert s in content, f"Schema '{s}' not found in documentation"


def test_doc_contains_error_codes():
    with open("API_DOCUMENTATION.md") as f:
        content = f.read()
    for code in ["400", "404", "422", "500"]:
        assert code in content, f"Error code {code} not in documentation"


def test_doc_contains_examples():
    with open("API_DOCUMENTATION.md") as f:
        content = f.read()
    assert "Example" in content or "example" in content
    assert "```http" in content
    assert "```json" in content


def test_doc_has_toc():
    with open("API_DOCUMENTATION.md") as f:
        content = f.read()
    assert "## Table of Contents" in content


def test_doc_has_data_schemas_section():
    with open("API_DOCUMENTATION.md") as f:
        content = f.read()
    assert "## Data Schemas" in content


# ── Verify the actual API works ──────────────

def test_create_user_integration():
    resp = client.post("/users", json={
        "name": "Bob Builder",
        "email": "bob@build.com",
        "age": 35,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Bob Builder"
    assert data["id"] == 1


def test_list_users_integration():
    client.post("/users", json={"name": "Alice", "email": "a@b.com", "age": 25})
    resp = client.get("/users")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_user_integration():
    create = client.post("/users", json={"name": "Alice", "email": "a@b.com", "age": 25})
    uid = create.json()["id"]
    resp = client.get(f"/users/{uid}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"


def test_update_user_integration():
    create = client.post("/users", json={"name": "Alice", "email": "a@b.com", "age": 25})
    uid = create.json()["id"]
    resp = client.put(f"/users/{uid}", json={"name": "Alice Updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice Updated"


def test_delete_user_integration():
    create = client.post("/users", json={"name": "Alice", "email": "a@b.com", "age": 25})
    uid = create.json()["id"]
    resp = client.delete(f"/users/{uid}")
    assert resp.status_code == 204
    resp2 = client.get(f"/users/{uid}")
    assert resp2.status_code == 404


def test_create_product_integration():
    resp = client.post("/products", json={
        "name": "Widget",
        "description": "A useful widget",
        "price": "9.99",
        "stock": 100,
    })
    assert resp.status_code == 201


def test_create_order_integration():
    # Create a user first
    client.post("/users", json={"name": "Alice", "email": "a@b.com", "age": 25})
    # Create a product
    client.post("/products", json={"name": "Widget", "description": "", "price": "9.99", "stock": 10})
    resp = client.post("/orders", json={
        "user_id": 1,
        "items": [{"product_id": 1, "quantity": 2, "unit_price": "9.99"}],
        "shipping_address": "123 Test St",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert float(data["total"]) == 19.98


def test_404_on_nonexistent_user():
    resp = client.get("/users/999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_validation_error_on_bad_data():
    resp = client.post("/users", json={"name": "X", "email": "invalid", "age": 0})
    assert resp.status_code == 422
