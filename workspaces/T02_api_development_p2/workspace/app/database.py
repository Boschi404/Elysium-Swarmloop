"""In-memory product store with thread-safe operations.

Provides CRUD operations backed by a dict, suitable for development/testing.
All operations acquire a lock to ensure safety under concurrent access.
"""

import threading
from datetime import datetime, timezone
from typing import Optional

from app.models import ProductCreate, ProductUpdate, ProductResponse


class ProductDatabase:
    """Thread-safe in-memory product repository."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._products: dict[int, dict] = {}
        self._next_id: int = 1

    def create(self, data: ProductCreate) -> ProductResponse:
        """Insert a new product and return it with assigned id and timestamp."""
        with self._lock:
            product_id = self._next_id
            self._next_id += 1
            now = datetime.now(timezone.utc)
            record = {
                "id": product_id,
                "name": data.name,
                "price": data.price,
                "category": data.category,
                "created_at": now,
            }
            self._products[product_id] = record
            return ProductResponse(**record)

    def get_by_id(self, product_id: int) -> Optional[ProductResponse]:
        """Return a product by id, or None if not found."""
        with self._lock:
            record = self._products.get(product_id)
            if record is None:
                return None
            return ProductResponse(**record)

    def list(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[ProductResponse], int]:
        """Return a filtered, paginated list of products and the total count.

        Filters are applied in order: category → min_price → max_price.
        """
        with self._lock:
            records = list(self._products.values())

        # Apply filters
        if category is not None:
            records = [r for r in records if r["category"] == category]
        if min_price is not None:
            records = [r for r in records if r["price"] >= min_price]
        if max_price is not None:
            records = [r for r in records if r["price"] <= max_price]

        # Sort by id for deterministic ordering
        records.sort(key=lambda r: r["id"])

        total = len(records)

        # Paginate
        start = (page - 1) * limit
        end = start + limit
        page_records = records[start:end]

        items = [ProductResponse(**r) for r in page_records]
        return items, total

    def update(self, product_id: int, data: ProductUpdate) -> Optional[ProductResponse]:
        """Replace a product's data entirely (PUT semantics).

        Returns the updated product, or None if not found.
        """
        with self._lock:
            record = self._products.get(product_id)
            if record is None:
                return None
            record["name"] = data.name
            record["price"] = data.price
            record["category"] = data.category
            # created_at stays unchanged
            return ProductResponse(**record)

    def delete(self, product_id: int) -> bool:
        """Delete a product by id. Returns True if deleted, False if not found."""
        with self._lock:
            if product_id not in self._products:
                return False
            del self._products[product_id]
            return True

    def count(self) -> int:
        """Return the total number of products in the store."""
        with self._lock:
            return len(self._products)


# Singleton instance
db = ProductDatabase()
