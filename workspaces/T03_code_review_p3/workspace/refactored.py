"""
Refactored code — all 5 anti-patterns fixed.

Fixes applied:
  1. God Object → Split into focused classes (TaxCalculator, DiscountCalculator,
     InvoiceService, ReceiptService, EmailService, InventoryService, OrderProcessor)
  2. Magic Numbers → Named constants (TAX_RATE, DISCOUNT_RATE, etc.)
  3. Shotgun Surgery → Single source of truth (TAX_RATE constant)
  4. Copy-Paste Duplication → Shared _build_document_lines() helper
  5. Boolean Trap Parameter → Keyword-only arguments
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum, auto
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# Named constants — eliminates magic numbers + shotgun surgery
# ──────────────────────────────────────────────────────────────────────────────
TAX_RATE = Decimal("0.10")
DISCOUNT_RATE = Decimal("0.20")
DISCOUNT_THRESHOLD = Decimal("100.00")
RESTOCK_THRESHOLD = 50
RESTOCK_QTY = 50
PAYMENT_DUE_DAYS = 30
ACTIVE_THRESHOLD = 7


# ──────────────────────────────────────────────────────────────────────────────
# Enum for document type — eliminates copy-paste
# ──────────────────────────────────────────────────────────────────────────────
class DocumentType(Enum):
    INVOICE = auto()
    RECEIPT = auto()


# ──────────────────────────────────────────────────────────────────────────────
# Dedicated calculators — extracted from the God Object
# ──────────────────────────────────────────────────────────────────────────────
class TaxCalculator:
    """Single-responsibility: calculates tax."""

    @staticmethod
    def calculate(subtotal: Decimal) -> Decimal:
        return (subtotal * TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class DiscountCalculator:
    """Single-responsibility: calculates discounts."""

    @staticmethod
    def calculate(total: Decimal) -> Decimal:
        if total > DISCOUNT_THRESHOLD:
            return (total * DISCOUNT_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Decimal("0.00")


class InventoryService:
    """Single-responsibility: manages stock."""

    def __init__(self):
        self._log = []

    def ensure_stock(self, items: list[dict]) -> None:
        for item in items:
            if item["stock"] < RESTOCK_THRESHOLD:
                self._restock(item)

    def _restock(self, item: dict) -> None:
        needed = RESTOCK_QTY - item["stock"]
        item["stock"] = RESTOCK_QTY
        self._log.append(f"Restocked item {item['id']} by {needed}")

    @property
    def log(self) -> list[str]:
        return list(self._log)


class EmailService:
    """Single-responsibility: sends notifications."""

    def __init__(self):
        self.sent = []

    def send_order_confirmation(self, order: dict, result: dict) -> None:
        self.sent.append(f"Order {order['id']} confirmation sent")
        # In production this would call an email API.

    def send_bulk(self, orders: list[dict], results: list[dict]) -> None:
        for order, result in zip(orders, results):
            self.send_order_confirmation(order, result)


class ReportingService:
    """Single-responsibility: aggregates reports."""

    @staticmethod
    def build_report(orders: list[dict]) -> dict:
        total_revenue = sum(o["total"] for o in orders)
        total_orders = len(orders)
        avg_order = total_revenue / total_orders if total_orders > 0 else Decimal("0.00")
        return {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "average_order": round(avg_order, 2),
            "status": "active" if total_orders > ACTIVE_THRESHOLD else "idle",
        }


# ──────────────────────────────────────────────────────────────────────────────
# Document generation — eliminated copy-paste duplication
# ──────────────────────────────────────────────────────────────────────────────
def _build_document_lines(doc_type: DocumentType, order: dict) -> list[str]:
    """Shared template for both invoices and receipts.

    The only variable parts are the heading and the final line.
    Everything else is written ONCE.
    """
    tax = TaxCalculator.calculate(Decimal(str(order["total"])))
    total_with_tax = Decimal(str(order["total"])) + tax
    discount = DiscountCalculator.calculate(total_with_tax)
    grand_total = total_with_tax - discount

    heading = "INVOICE" if doc_type == DocumentType.INVOICE else "RECEIPT"
    closing = (
        f"Due: within {PAYMENT_DUE_DAYS} days"
        if doc_type == DocumentType.INVOICE
        else "Paid: today"
    )

    return [
        f"{heading} #{order['id']}",
        f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        f"Items: {len(order.get('items', []))}",
        f"Subtotal: ${order['total']:.2f}",
        f"Tax: ${tax:.2f}",
        f"Discount: ${discount:.2f}",
        f"Total: ${grand_total:.2f}",
        closing,
    ]


class InvoiceService:
    @staticmethod
    def generate(order: dict) -> str:
        return "\n".join(_build_document_lines(DocumentType.INVOICE, order))


class ReceiptService:
    @staticmethod
    def generate(order: dict) -> str:
        return "\n".join(_build_document_lines(DocumentType.RECEIPT, order))


# ──────────────────────────────────────────────────────────────────────────────
# OrderProcessor — now only handles order processing (single responsibility)
# ──────────────────────────────────────────────────────────────────────────────
class OrderProcessor:
    """Processes orders by delegating to specialised services.

    Responsibilities:
      - Validate input
      - Coordinate calculation (tax → discount → total)
      - Persist processed order
      - Optionally trigger notifications

    Two boolean parameters remain (send_email, notify), but they are now
    KEYWORD-ONLY — callers MUST write send_email=True, so the meaning is clear.
    """

    def __init__(
        self,
        inventory: Optional[InventoryService] = None,
        email: Optional[EmailService] = None,
    ):
        self.inventory = inventory or InventoryService()
        self.email = email or EmailService()
        self._orders: list[dict] = []

    @property
    def orders(self) -> list[dict]:
        return list(self._orders)

    def process_order(self, order: dict, *, send_email: bool = False) -> dict:
        """Process a single order.

        Args:
            order: Order dict with 'id', 'items', 'total'.
            send_email:  Keyword-only — forces explicit ``send_email=True`` at call site.

        Returns:
            Processed order summary.
        """
        # ── Validation ──────────────────────────────────────────────────
        if not order.get("items"):
            raise ValueError("Order has no items")
        if order.get("total", 0) <= 0:
            raise ValueError("Invalid total")

        subtotal = Decimal(str(order["total"]))

        # ── Calculation (delegated) ─────────────────────────────────────
        tax = TaxCalculator.calculate(subtotal)
        total_with_tax = subtotal + tax
        discount = DiscountCalculator.calculate(total_with_tax)
        grand_total = total_with_tax - discount

        # ── Inventory ───────────────────────────────────────────────────
        self.inventory.ensure_stock(order["items"])

        # ── Build result ────────────────────────────────────────────────
        result = {
            "order_id": order["id"],
            "subtotal": float(subtotal),
            "tax": float(tax),
            "discount": float(discount),
            "total": float(grand_total),
            "status": "processed",
        }
        self._orders.append(result)

        # ── Notification (keyword-only — self-documenting) ─────────────
        if send_email:
            self.email.send_order_confirmation(order, result)

        return result

    def process_batch(self, orders: list[dict], *, notify: bool = False) -> list[dict]:
        """Process multiple orders.

        Args:
            orders: List of order dicts.
            notify: Keyword-only — forces ``notify=True`` to be explicit.

        Returns:
            List of processed order results.
        """
        results = []
        for order in orders:
            r = self.process_order(order, send_email=notify)
            results.append(r)
        return results
