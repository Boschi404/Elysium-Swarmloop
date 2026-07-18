"""
Refactored order processing module — clean code.
Eliminates: God Object, Magic Numbers, Shotgun Surgery, Copy-Paste, Boolean Trap.
"""
from dataclasses import dataclass
from typing import Optional


# =============================================================================
# Named Constants (eliminates Magic Numbers)
# =============================================================================

# Tax rates
TAX_RATES = {"gadget": 0.15, "widget": 0.10, "gizmo": 0.05, "doodad": 0.05}

# Discount thresholds & rates
DISCOUNT_POLICY: dict[str, tuple[int, float]] = {
    "gadget": (50, 0.05),
    "widget": (100, 0.02),
}

# Shipping
FREE_SHIPPING_WEIGHT = 100
STANDARD_SHIPPING_RATE = 0.02
URGENT_SURCHARGE_RATE = 0.05

# Refund
REFUND_RATE = 0.85
PARTIAL_REFUND_FACTOR = 0.5

# Report
HIGH_VOLUME_THRESHOLD = 250
REVENUE_BONUS_THRESHOLD = 10000

# Inventory defaults
INVENTORY_DEFAULTS = {"gadget": 50, "widget": 100, "gizmo": 25, "doodad": 200}


# =============================================================================
# Parameter object (eliminates Boolean Trap Parameter)
# =============================================================================

@dataclass
class OrderOptions:
    """Named options for order processing — self-documenting at call sites."""
    urgent: bool = False
    apply_warranty: bool = False
    gift_wrap: bool = False
    expedite: bool = False
    notify_customer: bool = True


# =============================================================================
# Single-responsibility services (eliminate God Object)
# =============================================================================

class InventoryManager:
    """Manages stock levels for all SKUs."""

    def __init__(self) -> None:
        self._stock: dict[str, int] = dict(INVENTORY_DEFAULTS)

    def reserve(self, sku: str, quantity: int) -> bool:
        """Reserve stock if sufficient exists. Returns False if insufficient."""
        if quantity <= 0:
            return False
        if self._stock.get(sku, 0) < quantity:
            return False
        self._stock[sku] -= quantity
        return True

    def check_stock(self, sku: str) -> int:
        """Return current stock level for a SKU."""
        return self._stock.get(sku, 0)


class Logger:
    """Minimal event logger."""

    def __init__(self) -> None:
        self.entries: list[str] = []

    def log(self, message: str) -> None:
        self.entries.append(message)

    def warning(self, message: str) -> None:
        self.entries.append(f"WARN: {message}")


class OrderProcessor:
    """Places and tracks orders."""

    def __init__(self, inventory: InventoryManager, logger: Logger) -> None:
        self._inventory = inventory
        self._logger = logger
        self.orders: list[tuple[str, int, float]] = []
        self.total_revenue: float = 0.0

    def place(self, sku: str, quantity: int, unit_price: float) -> bool:
        """Attempt to place an order. Returns True if successful."""
        if not self._inventory.reserve(sku, quantity):
            self._logger.warning(f"{sku} out of stock")
            return False
        line_total = unit_price * quantity
        self.orders.append((sku, quantity, line_total))
        self.total_revenue += line_total
        return True


class TaxCalculator:
    """Compute taxes based on item type."""

    @staticmethod
    def calculate(price: float, item_type: str) -> float:
        return price * TAX_RATES.get(item_type, 0.05)


class DiscountCalculator:
    """Compute volume discounts."""

    @staticmethod
    def calculate(price: float, item_type: str, quantity: int) -> float:
        policy = DISCOUNT_POLICY.get(item_type)
        if policy is None:
            return 0.0
        min_qty, rate = policy
        if quantity >= min_qty:
            return price * rate
        return 0.0


class ShippingCalculator:
    """Compute shipping costs — single source of truth for shipping rules."""

    def __init__(self, free_weight: int = FREE_SHIPPING_WEIGHT,
                 rate: float = STANDARD_SHIPPING_RATE,
                 surcharge: float = URGENT_SURCHARGE_RATE) -> None:
        self.free_weight = free_weight
        self.rate = rate
        self.surcharge = surcharge

    def calculate(self, items: list[tuple[str, int, float]], urgent: bool = False) -> float:
        """Edge case: empty items returns 0.0."""
        total_weight = sum(qty for _, qty, _ in items)
        if total_weight == 0:
            return 0.0
        if total_weight >= self.free_weight:
            cost = 0.0
        else:
            cost = total_weight * self.rate
        if urgent:
            cost += total_weight * self.surcharge
        return cost


class RefundService:
    """Handles refund calculations with a clear policy object."""

    def __init__(self, rate: float = REFUND_RATE,
                 partial_factor: float = PARTIAL_REFUND_FACTOR) -> None:
        self.rate = rate
        self.partial_factor = partial_factor

    def calculate(self, original_amount: float, partial: bool = False) -> float:
        """Edge case: 0 or negative amounts return 0."""
        if original_amount <= 0:
            return 0.0
        amount = original_amount * self.rate
        if partial:
            amount *= self.partial_factor
        return amount


class ReportService:
    """Generates business reports and summaries."""

    def __init__(self, high_volume: int = HIGH_VOLUME_THRESHOLD,
                 bonus_revenue: float = REVENUE_BONUS_THRESHOLD) -> None:
        self.high_volume = high_volume
        self.bonus_revenue = bonus_revenue

    def sales_report(self, orders: list, total_revenue: float) -> str:
        """Generate formatted sales report."""
        report = "--- SALES REPORT ---\n"
        if len(orders) > self.high_volume:
            report += "HIGH VOLUME: Consider bulk discounts.\n"
        report += f"Revenue: ${total_revenue:.2f}\n"
        report += f"Orders: {len(orders)}\n"
        return report

    def export_summary(self, orders: list, total_revenue: float) -> str:
        """Export order summary as CSV-like text."""
        lines = []
        for sku, qty, total in orders:
            lines.append(f"{sku}: qty={qty} total=${total:.2f}")
        if total_revenue > self.bonus_revenue:
            lines.append("BONUS: Revenue threshold exceeded!")
        return "\n".join(lines)


# =============================================================================
# Facade (thin coordinator, NOT a God Object)
# =============================================================================

class OrderFacade:
    """Thin coordinator that wires services together — does not own business logic."""

    def __init__(self) -> None:
        self.logger = Logger()
        self.inventory = InventoryManager()
        self.orders = OrderProcessor(self.inventory, self.logger)
        self.tax = TaxCalculator()
        self.discount = DiscountCalculator()
        self.shipping = ShippingCalculator()
        self.refund_service = RefundService()
        self.reports = ReportService()

    def process_order(self, customer: str, items: list[tuple[str, int, float]],
                      options: Optional[OrderOptions] = None) -> dict:
        """Process an order with explicit options — no boolean trap."""
        opts = options or OrderOptions()
        for sku, qty, price in items:
            self.orders.place(sku, qty, price)

        shipping = self.shipping.calculate(items, urgent=opts.urgent)
        self.orders.total_revenue += shipping

        self.logger.log(f"Order for {customer}: {len(items)} items")
        return {
            "customer": customer,
            "items_count": len(items),
            "total": self.orders.total_revenue,
            "shipping": shipping,
        }

    def refund(self, order_index: int, reason: str, partial: bool = False) -> float:
        """Refund an order using the centralised RefundService."""
        if order_index < 0 or order_index >= len(self.orders.orders):
            return 0.0
        order = self.orders.orders[order_index]
        sku, qty, amount = order
        refund_amount = self.refund_service.calculate(amount, partial=partial)
        self.orders.total_revenue -= refund_amount
        self.logger.log(f"Refund: {sku} reason={reason} partial={partial}")
        return refund_amount
