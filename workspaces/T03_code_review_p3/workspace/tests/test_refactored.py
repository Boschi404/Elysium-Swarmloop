"""
Tests for the refactored order-processing code.

Verifies that extracted services work individually,
that the refactored OrderProcessor produces correct results,
and that the anti-patterns are truly eliminated.
"""

import sys
import os
from decimal import Decimal

# Ensure we can import from the workspace
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from refactored import (
    TAX_RATE,
    DISCOUNT_RATE,
    DISCOUNT_THRESHOLD,
    TaxCalculator,
    DiscountCalculator,
    InventoryService,
    EmailService,
    ReportingService,
    InvoiceService,
    ReceiptService,
    DocumentType,
    OrderProcessor,
    _build_document_lines,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_ORDER = {
    "id": 1001,
    "total": 200.00,
    "items": [
        {"id": 1, "name": "Widget", "price": 100.00, "stock": 60},
        {"id": 2, "name": "Gadget", "price": 100.00, "stock": 30},
    ],
}

SMALL_ORDER = {
    "id": 1002,
    "total": 50.00,
    "items": [{"id": 3, "name": "Clip", "price": 50.00, "stock": 200}],
}

EMPTY_ORDER = {"id": 9999, "total": 100.00, "items": []}
NEGATIVE_ORDER = {"id": 9998, "total": -10.00, "items": [{"id": 4, "name": "Bad", "price": -10.00, "stock": 1}]}


# ── Tests: Named constants (anti-pattern: magic numbers fixed) ───────────────

def test_tax_rate_is_named_constant():
    assert TAX_RATE == Decimal("0.10"), "Tax rate constant must be 10%"


def test_discount_rate_is_named_constant():
    assert DISCOUNT_RATE == Decimal("0.20"), "Discount rate constant must be 20%"


def test_discount_threshold_is_named_constant():
    assert DISCOUNT_THRESHOLD == Decimal("100.00"), "Discount threshold must be $100"


# ── Tests: TaxCalculator (single responsibility, no magic numbers) ───────────

class TestTaxCalculator:
    def test_calculates_tax_on_subtotal(self):
        assert TaxCalculator.calculate(Decimal("200.00")) == Decimal("20.00")

    def test_calculates_tax_on_small_amount(self):
        assert TaxCalculator.calculate(Decimal("1.00")) == Decimal("0.10")

    def test_rounds_to_two_decimals(self):
        result = TaxCalculator.calculate(Decimal("9.99"))
        assert result == Decimal("1.00"), f"Got {result}"


# ── Tests: DiscountCalculator (single responsibility, no magic numbers) ──────

class TestDiscountCalculator:
    def test_applies_discount_above_threshold(self):
        result = DiscountCalculator.calculate(Decimal("200.00"))
        expected = Decimal("200.00") * DISCOUNT_RATE
        assert result == expected.quantize(Decimal("0.01"))

    def test_no_discount_below_threshold(self):
        assert DiscountCalculator.calculate(Decimal("50.00")) == Decimal("0.00")

    def test_no_discount_at_threshold(self):
        assert DiscountCalculator.calculate(DISCOUNT_THRESHOLD) == Decimal("0.00")

    def test_applies_discount_just_above_threshold(self):
        result = DiscountCalculator.calculate(DISCOUNT_THRESHOLD + Decimal("0.01"))
        assert result > Decimal("0.00")


# ── Tests: InventoryService (single responsibility) ──────────────────────────

class TestInventoryService:
    def test_restocks_low_stock_items(self):
        svc = InventoryService()
        items = [{"id": 1, "stock": 10}]
        svc.ensure_stock(items)
        assert items[0]["stock"] == 50

    def test_does_not_restock_high_stock_items(self):
        svc = InventoryService()
        items = [{"id": 1, "stock": 100}]
        svc.ensure_stock(items)
        assert items[0]["stock"] == 100

    def test_logs_restocks(self):
        svc = InventoryService()
        items = [{"id": 5, "stock": 10}]
        svc.ensure_stock(items)
        assert len(svc.log) == 1


# ── Tests: EmailService (single responsibility, no booleans) ─────────────────

class TestEmailService:
    def test_send_confirmation(self):
        svc = EmailService()
        svc.send_order_confirmation(SAMPLE_ORDER, {})
        assert len(svc.sent) == 1
        assert "1001" in svc.sent[0]

    def test_send_bulk(self):
        svc = EmailService()
        orders = [SAMPLE_ORDER, SMALL_ORDER]
        svc.send_bulk(orders, [{}, {}])
        assert len(svc.sent) == 2


# ── Tests: ReportingService (single responsibility) ──────────────────────────

class TestReportingService:
    def test_empty_orders(self):
        report = ReportingService.build_report([])
        assert report["total_orders"] == 0
        assert report["total_revenue"] == 0
        assert report["average_order"] == 0

    def test_reports_status_active_above_threshold(self):
        processed = [{"total": Decimal(str(i))} for i in range(1, 12)]
        report = ReportingService.build_report(processed)
        assert report["status"] == "active"

    def test_reports_status_idle_below_threshold(self):
        processed = [{"total": Decimal("100.00")} for _ in range(3)]
        report = ReportingService.build_report(processed)
        assert report["status"] == "idle"

    def test_average_order_calculation(self):
        processed = [
            {"total": Decimal("100.00")},
            {"total": Decimal("200.00")},
        ]
        report = ReportingService.build_report(processed)
        assert report["average_order"] == 150.0


# ── Tests: Document generation (anti-pattern: copy-paste duplication fixed) ──

class TestDocumentGeneration:
    def test_invoice_has_correct_heading(self):
        doc = InvoiceService.generate(SAMPLE_ORDER)
        assert doc.startswith("INVOICE #1001")

    def test_receipt_has_correct_heading(self):
        doc = ReceiptService.generate(SAMPLE_ORDER)
        assert doc.startswith("RECEIPT #1001")

    def test_invoice_mentions_due_days(self):
        doc = InvoiceService.generate(SAMPLE_ORDER)
        assert "Due: within" in doc
        assert "Paid: today" not in doc

    def test_receipt_mentions_paid_today(self):
        doc = ReceiptService.generate(SAMPLE_ORDER)
        assert "Paid: today" in doc
        assert "Due: within" not in doc

    def test_both_have_same_numeric_values(self):
        invoice = InvoiceService.generate(SAMPLE_ORDER)
        receipt = ReceiptService.generate(SAMPLE_ORDER)
        # Remove heading and last line — compare the middle
        inv_lines = invoice.splitlines()[1:-1]
        rec_lines = receipt.splitlines()[1:-1]
        assert inv_lines == rec_lines


# ── Tests: OrderProcessor (no God Object, no boolean traps) ──────────────────

class TestOrderProcessor:
    def test_processes_order_correctly(self):
        processor = OrderProcessor()
        result = processor.process_order(SAMPLE_ORDER)
        assert result["order_id"] == 1001
        assert result["status"] == "processed"
        assert result["subtotal"] == 200.00
        assert result["tax"] == 20.00
        assert result["discount"] == 44.00  # 20% of (200+20) = 44
        assert result["total"] == 176.00    # 200 + 20 - 44

    def test_raises_on_empty_items(self):
        processor = OrderProcessor()
        try:
            processor.process_order(EMPTY_ORDER)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "items" in str(e)

    def test_raises_on_negative_total(self):
        processor = OrderProcessor()
        try:
            processor.process_order(NEGATIVE_ORDER)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid total" in str(e)

    def test_keyword_only_send_email(self):
        """Calling with positional True should fail (keyword-only enforced)."""
        processor = OrderProcessor()
        try:
            # This should raise a TypeError: send_email is keyword-only
            processor.process_order(SAMPLE_ORDER, True)
            assert False, "Should have raised TypeError"
        except TypeError:
            pass  # Expected — keyword-only enforced

    def test_keyword_email_works(self):
        processor = OrderProcessor()
        result = processor.process_order(SAMPLE_ORDER, send_email=True)
        assert result["status"] == "processed"
        assert len(processor.email.sent) == 1

    def test_no_email_by_default(self):
        processor = OrderProcessor()
        processor.process_order(SAMPLE_ORDER)
        assert len(processor.email.sent) == 0

    def test_processes_batch(self):
        processor = OrderProcessor()
        results = processor.process_batch([SAMPLE_ORDER, SMALL_ORDER])
        assert len(results) == 2
        assert results[0]["order_id"] == 1001
        assert results[1]["order_id"] == 1002

    def test_batch_notify_keyword_only(self):
        """notify must be keyword-only."""
        processor = OrderProcessor()
        try:
            processor.process_batch([SAMPLE_ORDER], True)
            assert False, "Should have raised TypeError"
        except TypeError:
            pass

    def test_orders_property_returns_copy(self):
        processor = OrderProcessor()
        processor.process_order(SAMPLE_ORDER)
        assert len(processor.orders) == 1
        # Modifying the returned list should not affect internal state
        processor.orders.clear()
        assert len(processor.orders) == 1  # Internal state unchanged
        # Internal list should still have the original order
        processor.process_order(SMALL_ORDER)
        assert len(processor.orders) == 2  # Original + new


# ── Tests: Anti-pattern verification (meta-tests) ────────────────────────────

class TestAntiPatternVerification:
    def test_no_magic_numbers_in_constants(self):
        """All meaningful numeric values are named constants."""
        assert hasattr(sys.modules["refactored"], "TAX_RATE")
        assert hasattr(sys.modules["refactored"], "DISCOUNT_RATE")
        assert hasattr(sys.modules["refactored"], "DISCOUNT_THRESHOLD")
        assert hasattr(sys.modules["refactored"], "RESTOCK_THRESHOLD")
        assert hasattr(sys.modules["refactored"], "PAYMENT_DUE_DAYS")
        assert hasattr(sys.modules["refactored"], "ACTIVE_THRESHOLD")

    def test_single_tax_rate_source(self):
        """TaxCalculator and document builders all use the same constant."""
        calc_result = TaxCalculator.calculate(Decimal("100.00"))
        expected = Decimal("100.00") * TAX_RATE
        assert calc_result == expected.quantize(Decimal("0.01"))

    def test_shared_build_document_lines_function(self):
        """Invoice and Receipt share the same template function."""
        inv_lines = _build_document_lines(DocumentType.INVOICE, SAMPLE_ORDER)
        rec_lines = _build_document_lines(DocumentType.RECEIPT, SAMPLE_ORDER)
        # Middle lines (indices 1 to -1) must be identical
        assert inv_lines[1:-1] == rec_lines[1:-1], "Shared body must be identical"
        # Only heading and closing differ
        assert inv_lines[0] != rec_lines[0]
        assert inv_lines[-1] != rec_lines[-1]
