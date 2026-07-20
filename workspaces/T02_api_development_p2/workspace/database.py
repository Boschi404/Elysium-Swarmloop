"""In-memory database for product storage."""

from typing import Optional
from models import Product, ProductCreate, ProductUpdate, generate_id


class ProductDatabase:
    """Thread-safe in-memory product store."""

    def __init__(self):
        self._products: dict[str, Product] = {}

    def list_products(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[Product], int]:
        """Return (filtered_products, total_count) with pagination."""
        items = list(self._products.values())

        # Apply filters
        if category:
            items = [p for p in items if p.category.lower() == category.lower()]
        if min_price is not None:
            items = [p for p in items if p.price >= min_price]
        if max_price is not None:
            items = [p for p in items if p.price <= max_price]

        # Sort by name for deterministic pagination
        items.sort(key=lambda p: (p.name.lower(), p.id))

        total = len(items)

        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        items = items[start:end]

        return items, total

    def get_product(self, product_id: str) -> Optional[Product]:
        """Return a product by ID, or None."""
        return self._products.get(product_id)

    def create_product(self, data: ProductCreate) -> Product:
        """Create a new product and return it."""
        product = Product(id=generate_id(), **data.model_dump())
        self._products[product.id] = product
        return product

    def update_product(self, product_id: str, data: ProductUpdate) -> Optional[Product]:
        """Update an existing product. Returns None if not found."""
        existing = self._products.get(product_id)
        if existing is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        updated = Product(**{**existing.model_dump(), **update_data})
        self._products[product_id] = updated
        return updated

    def delete_product(self, product_id: str) -> bool:
        """Delete a product by ID. Returns True if existed."""
        if product_id in self._products:
            del self._products[product_id]
            return True
        return False


# Singleton instance
db = ProductDatabase()
