"""In-memory storage for Users, Products, and Orders."""
from datetime import datetime
from typing import Any
from decimal import Decimal


class InMemoryDB:
    """Simple in-memory database with auto-incrementing IDs."""

    def __init__(self):
        self._users: dict[int, dict[str, Any]] = {}
        self._products: dict[int, dict[str, Any]] = {}
        self._orders: dict[int, dict[str, Any]] = {}
        self._next_ids = {"user": 1, "product": 1, "order": 1}

    # ── Users ──────────────────────────────────

    def list_users(self) -> list[dict[str, Any]]:
        return list(self._users.values())

    def get_user(self, user_id: int) -> dict[str, Any] | None:
        return self._users.get(user_id)

    def create_user(self, data: dict[str, Any]) -> dict[str, Any]:
        now = datetime.utcnow()
        uid = self._next_ids["user"]
        self._next_ids["user"] += 1
        user = {
            "id": uid,
            **data,
            "created_at": now,
            "updated_at": now,
        }
        self._users[uid] = user
        return user

    def update_user(self, user_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
        current = self._users.get(user_id)
        if current is None:
            return None
        updates["updated_at"] = datetime.utcnow()
        current.update(updates)
        return current

    def delete_user(self, user_id: int) -> bool:
        if user_id not in self._users:
            return False
        del self._users[user_id]
        return True

    # ── Products ───────────────────────────────

    def list_products(self) -> list[dict[str, Any]]:
        return list(self._products.values())

    def get_product(self, product_id: int) -> dict[str, Any] | None:
        return self._products.get(product_id)

    def create_product(self, data: dict[str, Any]) -> dict[str, Any]:
        now = datetime.utcnow()
        pid = self._next_ids["product"]
        self._next_ids["product"] += 1
        product = {
            "id": pid,
            **data,
            "created_at": now,
            "updated_at": now,
        }
        self._products[pid] = product
        return product

    def update_product(self, product_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
        current = self._products.get(product_id)
        if current is None:
            return None
        updates["updated_at"] = datetime.utcnow()
        current.update(updates)
        return current

    # ── Orders ─────────────────────────────────

    def create_order(self, data: dict[str, Any]) -> dict[str, Any]:
        now = datetime.utcnow()
        oid = self._next_ids["order"]
        self._next_ids["order"] += 1
        # Compute total from items
        total = sum(
            Decimal(str(item["unit_price"])) * item["quantity"]
            for item in data["items"]
        )
        order = {
            "id": oid,
            **data,
            "total": total,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
        }
        self._orders[oid] = order
        return order

    def get_order(self, order_id: int) -> dict[str, Any] | None:
        return self._orders.get(order_id)

    def reset(self):
        """Clear all data (for testing)."""
        self._users.clear()
        self._products.clear()
        self._orders.clear()
        self._next_ids = {"user": 1, "product": 1, "order": 1}


db = InMemoryDB()
