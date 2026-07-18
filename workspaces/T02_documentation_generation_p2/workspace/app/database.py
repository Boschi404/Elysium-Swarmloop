"""In-memory database for the FastAPI application."""

from datetime import datetime, timezone
from app.models import (
    User, UserCreate, Product, ProductCreate, ProductUpdate,
    Order, OrderCreate, OrderUpdate, OrderItemResponse,
    OrderStatus
)


class Database:
    """Simple in-memory database with auto-increment IDs."""

    def __init__(self):
        self._users: dict[int, User] = {}
        self._products: dict[int, Product] = {}
        self._orders: dict[int, Order] = {}
        self._next_user_id = 1
        self._next_product_id = 1
        self._next_order_id = 1
        self._seed()

    def _seed(self):
        """Seed with sample data."""
        # Users
        u1 = User(id=1, name="Alice Rossi", email="alice@example.com", role="admin",
                  created_at=datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc))
        u2 = User(id=2, name="Bob Bianchi", email="bob@example.com", role="customer",
                  created_at=datetime(2025, 2, 20, 14, 30, 0, tzinfo=timezone.utc))
        u3 = User(id=3, name="Chiara Verdi", email="chiara@example.com", role="customer",
                  created_at=datetime(2025, 3, 10, 9, 15, 0, tzinfo=timezone.utc))
        self._users = {1: u1, 2: u2, 3: u3}
        self._next_user_id = 4

        # Products
        p1 = Product(id=1, name="Wireless Mouse", description="Ergonomic wireless mouse with USB receiver",
                     price=29.99, stock=150, category="electronics",
                     created_at=datetime(2025, 1, 10, 8, 0, 0, tzinfo=timezone.utc))
        p2 = Product(id=2, name="Mechanical Keyboard", description="RGB mechanical keyboard with Cherry MX switches",
                     price=89.99, stock=75, category="electronics",
                     created_at=datetime(2025, 1, 12, 9, 0, 0, tzinfo=timezone.utc))
        p3 = Product(id=3, name="USB-C Hub", description="7-in-1 USB-C hub with HDMI, USB-A, SD card reader",
                     price=39.99, stock=200, category="electronics",
                     created_at=datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc))
        p4 = Product(id=4, name="Notebook A5", description="Hardcover dotted notebook, 200 pages",
                     price=12.50, stock=500, category="stationery",
                     created_at=datetime(2025, 2, 1, 11, 0, 0, tzinfo=timezone.utc))
        p5 = Product(id=5, name="Desk Lamp", description="LED desk lamp with adjustable brightness and color temp",
                     price=45.00, stock=60, category="furniture",
                     created_at=datetime(2025, 2, 15, 12, 0, 0, tzinfo=timezone.utc))
        self._products = {1: p1, 2: p2, 3: p3, 4: p4, 5: p5}
        self._next_product_id = 6

        # Orders
        o1 = Order(
            id=1, user_id=1,
            items=[OrderItemResponse(product_id=1, product_name="Wireless Mouse", quantity=2, unit_price=29.99),
                   OrderItemResponse(product_id=3, product_name="USB-C Hub", quantity=1, unit_price=39.99)],
            total=99.97, status=OrderStatus.delivered,
            created_at=datetime(2025, 3, 1, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 3, 5, 16, 0, 0, tzinfo=timezone.utc)
        )
        o2 = Order(
            id=2, user_id=2,
            items=[OrderItemResponse(product_id=2, product_name="Mechanical Keyboard", quantity=1, unit_price=89.99)],
            total=89.99, status=OrderStatus.shipped,
            created_at=datetime(2025, 3, 20, 14, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2025, 3, 22, 9, 0, 0, tzinfo=timezone.utc)
        )
        self._orders = {1: o1, 2: o2}
        self._next_order_id = 3

    # ─── Users ───────────────────────────────────────────────

    def get_users(self) -> list[User]:
        return list(self._users.values())

    def get_user(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def create_user(self, data: UserCreate) -> User:
        uid = self._next_user_id
        self._next_user_id += 1
        user = User(
            id=uid,
            name=data.name,
            email=data.email,
            role=data.role,
            created_at=datetime.now(timezone.utc)
        )
        self._users[uid] = user
        return user

    # ─── Products ───────────────────────────────────────────

    def get_products(self) -> list[Product]:
        return list(self._products.values())

    def get_product(self, product_id: int) -> Product | None:
        return self._products.get(product_id)

    def create_product(self, data: ProductCreate) -> Product:
        pid = self._next_product_id
        self._next_product_id += 1
        product = Product(
            id=pid,
            name=data.name,
            description=data.description,
            price=data.price,
            stock=data.stock,
            category=data.category,
            created_at=datetime.now(timezone.utc)
        )
        self._products[pid] = product
        return product

    def update_product(self, product_id: int, data: ProductUpdate) -> Product | None:
        existing = self._products.get(product_id)
        if existing is None:
            return None
        updated = Product(
            id=existing.id,
            name=data.name if data.name is not None else existing.name,
            description=data.description if data.description is not None else existing.description,
            price=data.price if data.price is not None else existing.price,
            stock=data.stock if data.stock is not None else existing.stock,
            category=data.category if data.category is not None else existing.category,
            created_at=existing.created_at
        )
        self._products[product_id] = updated
        return updated

    def delete_product(self, product_id: int) -> bool:
        if product_id in self._products:
            del self._products[product_id]
            return True
        return False

    # ─── Orders ─────────────────────────────────────────────

    def get_orders(self) -> list[Order]:
        return list(self._orders.values())

    def get_order(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)

    def create_order(self, data: OrderCreate) -> Order:
        oid = self._next_order_id
        self._next_order_id += 1
        now = datetime.now(timezone.utc)
        items_response: list[OrderItemResponse] = []
        total = 0.0
        for item in data.items:
            product = self._products.get(item.product_id)
            name = product.name if product else f"Product#{item.product_id}"
            price = product.price if product else 0.0
            items_response.append(OrderItemResponse(
                product_id=item.product_id,
                product_name=name,
                quantity=item.quantity,
                unit_price=price
            ))
            total += price * item.quantity
        order = Order(
            id=oid,
            user_id=data.user_id,
            items=items_response,
            total=round(total, 2),
            status=OrderStatus.pending,
            created_at=now,
            updated_at=now
        )
        self._orders[oid] = order
        return order

    def update_order(self, order_id: int, data: OrderUpdate) -> Order | None:
        existing = self._orders.get(order_id)
        if existing is None:
            return None
        updated = Order(
            id=existing.id,
            user_id=existing.user_id,
            items=existing.items,
            total=existing.total,
            status=data.status,
            created_at=existing.created_at,
            updated_at=datetime.now(timezone.utc)
        )
        self._orders[order_id] = updated
        return updated

    def delete_order(self, order_id: int) -> bool:
        if order_id in self._orders:
            del self._orders[order_id]
            return True
        return False


db = Database()
