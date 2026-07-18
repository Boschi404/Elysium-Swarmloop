"""
Original code containing 5 intentional anti-patterns.

Anti-patterns present:
  1. God Object (OrderProcessor does everything)
  2. Magic Numbers (hardcoded 0.1, 0.2, 100, 50, 7, 30)
  3. Shotgun Surgery (tax rate appears in 3 separate places)
  4. Copy-Paste Duplication (invoice vs receipt logic identical)
  5. Boolean Trap Parameter (process_order(..., send_email=True))
"""

import json
from datetime import datetime, timedelta
from typing import Optional


class OrderProcessor:
    """GOD OBJECT: This class does order processing, invoicing,
    inventory updates, email sending, reporting, and logging."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.orders = []
        self.log = []

    def process_order(self, order: dict, send_email: bool = False) -> dict:
        """Boolean trap: caller can't tell what True/False means at call site.
        Also shotgun surgery: tax rate 0.1 used inline."""
        # Validate
        if not order.get("items"):
            raise ValueError("Order has no items")
        if order.get("total", 0) <= 0:
            raise ValueError("Invalid total")

        # MUTATION BUG: calculates tax on total including existing tax
        tax = order["total"] * 0.1  # MAGIC NUMBER: 0.1 = 10% tax rate
        total_with_tax = order["total"] + tax

        # MUTATION BUG: applies flat discount without checking total
        discount = total_with_tax * 0.2 if total_with_tax > 100 else 0  # MAGIC NUMBERS: 0.2, 100
        grand_total = total_with_tax - discount

        # Update inventory — shotgun surgery: stock check threshold 50
        for item in order["items"]:
            if item["stock"] < 50:  # MAGIC NUMBER: stock threshold
                self._restock_item(item["id"], item["stock"] + 50)

        # Build result
        result = {
            "order_id": order["id"],
            "subtotal": order["total"],
            "tax": tax,
            "discount": discount,
            "total": grand_total,
            "status": "processed",
        }
        self.orders.append(result)

        if send_email:  # Boolean trap: what does True mean here?
            self._send_order_email(order, result)

        self._log(f"Processed order {order['id']}")
        return result

    def generate_invoice(self, order: dict) -> str:
        # COPY-PASTE DUPLICATION: nearly identical to generate_receipt
        # Shotgun surgery: tax 0.1 again
        tax = order["total"] * 0.1  # MAGIC NUMBER repeated
        total_with_tax = order["total"] + tax
        discount = total_with_tax * 0.2 if total_with_tax > 100 else 0
        grand_total = total_with_tax - discount

        lines = [
            f"INVOICE #{order['id']}",
            f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"Items: {len(order.get('items', []))}",
            f"Subtotal: ${order['total']:.2f}",
            f"Tax: ${tax:.2f}",
            f"Discount: ${discount:.2f}",
            f"Total: ${grand_total:.2f}",
            f"Due: within 30 days",  # MAGIC NUMBER: 30
        ]
        return "\n".join(lines)

    def generate_receipt(self, order: dict) -> str:
        # COPY-PASTE DUPLICATION: nearly identical to generate_invoice
        # Shotgun surgery: tax 0.1 yet again
        tax = order["total"] * 0.1  # MAGIC NUMBER repeated third time
        total_with_tax = order["total"] + tax
        discount = total_with_tax * 0.2 if total_with_tax > 100 else 0
        grand_total = total_with_tax - discount

        lines = [
            f"RECEIPT #{order['id']}",
            f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"Items: {len(order.get('items', []))}",
            f"Subtotal: ${order['total']:.2f}",
            f"Tax: ${tax:.2f}",
            f"Discount: ${discount:.2f}",
            f"Total: ${grand_total:.2f}",
            f"Paid: today",  # Only diff from invoice
        ]
        return "\n".join(lines)

    def _send_order_email(self, order: dict, result: dict) -> None:
        # This method internally duplicates total calculation
        # for the email body — SHOTGUN SURGERY again
        tax = order["total"] * 0.1
        # ... email logic (simplified)
        self._log(f"Email sent for order {order['id']}")

    def _restock_item(self, item_id: int, quantity: int) -> None:
        self._log(f"Restocked item {item_id} to {quantity}")

    def _log(self, message: str) -> None:
        timestamp = datetime.now().isoformat()
        self.log.append(f"[{timestamp}] {message}")

    # SHOTGUN SURGERY: if tax rate changes, you must update:
    #   - process_order line 30
    #   - generate_invoice line 60
    #   - generate_receipt line 82
    #   - _send_order_email line 99

    def get_report(self) -> dict:
        """Another god-object method: reporting lives here too."""
        total_revenue = sum(o["total"] for o in self.orders)
        total_orders = len(self.orders)
        avg_order = total_revenue / total_orders if total_orders > 0 else 0
        report = {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "average_order": round(avg_order, 2),
            "log_count": len(self.log),
            "status": "active" if total_orders > 7 else "idle",  # MAGIC NUMBER: 7
        }
        return report

    def process_batch(self, orders: list[dict], notify: bool = False) -> list[dict]:
        """Boolean trap again: what does notify=True mean?"""
        results = []
        for order in orders:
            r = self.process_order(order, send_email=notify)
            results.append(r)
        return results
