# Code Review Report: Anti-Pattern Detection

**File:** `original.py` (88 lines)
**Reviewer:** Elysium Swarmloop
**Severity:** 5 anti-patterns found — 3 critical, 2 moderate

---

## 1. God Object — `OrderProcessor` (lines 17–123)

**Severity:** CRITICAL

**What it is:** The `OrderProcessor` class handles order processing, tax calculation, discount
calculation, inventory management, invoice generation, receipt generation, email sending,
reporting, and logging. This violates the **Single Responsibility Principle**.

**Why it's harmful:**
- Any change — even a comment fix — risks breaking unrelated functionality
- The class is impossible to test in isolation (you need orders, inventory, email all mocked)
- New team members can't understand 10+ responsibilities in one file
- When the class grows past 200 lines, it becomes unmaintainable

**Affected lines:** 17–123

**Refactor strategy:** Split into separate classes/ modules:
- `OrderProcessor` → order processing only (delegates to specialized services)
- `TaxCalculator` — standalone tax logic
- `DiscountCalculator` — standalone discount logic
- `InvoiceService` / `ReceiptService` — document generation
- `EmailService` — email notifications
- `InventoryService` — stock management
- `LoggerService` — logging (or use stdlib logging)
- `ReportingService` — reports

---

## 2. Magic Numbers — lines 30, 33, 36, 75, 82, 97, 112, 118

**Severity:** CRITICAL

| Line | Magic Number | Meaning | Refactor |
|------|-------------|---------|----------|
| 30 | `0.1` | Tax rate (10%) | `TAX_RATE = Decimal('0.10')` |
| 33 | `0.2` | Discount rate (20%) | `DISCOUNT_RATE = Decimal('0.20')` |
| 33 | `100` | Discount threshold | `DISCOUNT_THRESHOLD = Decimal('100.00')` |
| 36 | `50` | Restock threshold | `RESTOCK_THRESHOLD = 50` |
| 36 | `50` | Restock quantity | `RESTOCK_QTY = 50` |
| 75 | `30` | Payment due days | `PAYMENT_DUE_DAYS = 30` |
| 112 | `7` | Active threshold | `ACTIVE_THRESHOLD = 7` |

**Why it's harmful:**
- No one knows what `0.1` or `50` means without reading the business logic
- Changing a value requires finding every occurrence (see Shotgun Surgery below)
- The same number may mean different things in different contexts (line 36: `50`
  is both threshold AND restock quantity — coincidence or bug?)

**Refactor strategy:** Extract ALL magic numbers to named constants at the top of the file
(or a `config.py` module). Use `Decimal` for monetary values to avoid floating-point drift.

---

## 3. Shotgun Surgery — tax rate `0.1` at lines 30, 60, 82, 99

**Severity:** CRITICAL

**What it is:** The same business rule (tax rate = 10%) is hardcoded in 4 separate locations.
If the tax rate changes, a developer must remember to update ALL 4 places.

**Why it's harmful:**
- One missed update = inconsistent behaviour (invoice shows 10%, receipt shows 12%)
- No single source of truth for the tax rate
- The error won't be caught by compilation — only by manual QA or customer complaint

**Affected call sites:**
| Line | Function | Context |
|------|----------|---------|
| 30 | `process_order` | Order total calculation |
| 60 | `generate_invoice` | Invoice document |
| 82 | `generate_receipt` | Receipt document |
| 99 | `_send_order_email` | Email body |

**Refactor strategy:** Define `TAX_RATE = 0.10` once as a module-level constant. All 4
functions reference it. When the rate changes, one edit propagates everywhere.

---

## 4. Copy-Paste Duplication — `generate_invoice` vs `generate_receipt` (lines 53–87)

**Severity:** MODERATE

**What it is:** `generate_invoice()` (lines 53–75) and `generate_receipt()` (lines 77–87)
share ~95% identical code. The only difference is the document header (`INVOICE` vs
`RECEIPT`) and the final line (`Due: within 30 days` vs `Paid: today`).

**Why it's harmful:**
- 2× the code = 2× the bugs
- Any fix to the invoice layout must be manually replicated in receipt
- Eventually they drift apart and behaviour inconsistency appears
- Violates the **DRY (Don't Repeat Yourself)** principle

**Refactor strategy:** A single `_format_document(order, doc_type)` method that takes
a `DocumentType` enum (`INVOICE` or `RECEIPT`) and produces the appropriate output.
The shared body is written once.

---

## 5. Boolean Trap Parameter — `send_email=False` at line 22, `notify=False` at line 117

**Severity:** MODERATE

**What it is:** A boolean parameter whose meaning is opaque at the call site.

```python
# What does True mean here?
processor.process_order(order, True)        # sends email?
processor.process_order(order, False)       # doesn't?

# Same problem with process_batch
processor.process_batch(orders, True)       # notify what?
```

**Why it's harmful:**
- `process_order(order, True)` is not self-documenting — the reader must look up the
  method signature to understand what `True` enables
- Makes grep results useless ("True" appears everywhere in a codebase)
- A maintenance hazard: adding a second boolean creates the
  `process_order(order, True, False, True)` nightmare

**Affected lines:**
| Line | Signature | Call site example |
|------|-----------|-------------------|
| 22 | `def process_order(self, order, send_email=False)` | `processor.process_order(order, True)` |
| 117 | `def process_batch(self, orders, notify=False)` | `processor.process_batch(orders, True)` |

**Refactor strategy:** Replace each boolean with a keyword-only argument:
```python
def process_order(self, order: dict, *, send_email: bool = False) -> dict
```
This forces callers to write `process_order(order, send_email=True)` which is
self-documenting. Even better: use an enum or strategy pattern if the behaviour
is complex enough.

---

## Summary

| # | Anti-Pattern | Severity | Lines | Fix |
|---|-------------|----------|-------|-----|
| 1 | God Object | CRITICAL | 17–123 | Split into 8 focused classes |
| 2 | Magic Numbers | CRITICAL | 30, 33, 36, 75, 97, 112, 118 | Named constants + Decimal |
| 3 | Shotgun Surgery | CRITICAL | 30, 60, 82, 99 | Single tax-rate constant |
| 4 | Copy-Paste Duplication | MODERATE | 53–87 | Unify invoice/receipt |
| 5 | Boolean Trap Parameter | MODERATE | 22, 117 | Keyword-only args |
