-- =============================================================================
-- Schema & Sample Data for Multi-Table JOIN Report (T03_data_analysis_p3)
-- =============================================================================
-- Tables: customers, products, orders, order_items
-- Relationships:
--   orders.customer_id → customers.customer_id
--   order_items.order_id → orders.order_id
--   order_items.product_id → products.product_id
-- =============================================================================

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- --- customers ---
CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT    NOT NULL
);

-- --- products ---
CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT    NOT NULL,
    price        REAL    NOT NULL
);

-- --- orders ---
CREATE TABLE orders (
    order_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id  INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date   TEXT    NOT NULL   -- ISO date (YYYY-MM-DD)
);

-- --- order_items (line items) ---
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL CHECK (quantity > 0)
);

-- ======================= SAMPLE DATA =======================

-- Customers (8 total — 5 with orders, 3 without)
INSERT INTO customers (customer_name) VALUES
    ('Alice Rossi'),
    ('Marco Bianchi'),
    ('Sofia Verdi'),
    ('Luca Neri'),
    ('Giulia Gialli'),
    ('Paolo Blu'),         -- no orders
    ('Elena Viola'),       -- no orders
    ('Davide Arancione');  -- no orders

-- Products (5)
INSERT INTO products (product_name, price) VALUES
    ('Tavolo in rovere',     350.00),
    ('Sedia ergonomica',     120.50),
    ('Lampada da terra',      89.99),
    ('Scrivania in vetro',   450.00),
    ('Libreria componibile', 210.00);

-- Orders (9 total — 6 within last 30 days, 3 older)
-- Using DATE('now') so the sample stays relevant whenever this runs.

-- Recent orders (last 30 days)
INSERT INTO orders (customer_id, order_date) VALUES
    (1, DATE('now', '-2 days')),
    (1, DATE('now', '-5 days')),
    (2, DATE('now', '-1 days')),
    (3, DATE('now', '-10 days')),
    (4, DATE('now', '-3 days')),
    (5, DATE('now', '-15 days'));

-- Older orders (outside last 30 days)
INSERT INTO orders (customer_id, order_date) VALUES
    (2, DATE('now', '-45 days')),
    (3, DATE('now', '-60 days')),
    (4, DATE('now', '-90 days'));

-- Order items (one or more per recent order)
INSERT INTO order_items (order_id, product_id, quantity) VALUES
    -- Alice (customer 1): 2 recent orders
    (1, 1, 1),   -- 1× Tavolo in rovere
    (1, 2, 4),   -- 4× Sedia ergonomica
    (2, 3, 2),   -- 2× Lampada da terra
    -- Marco (customer 2): 1 recent order
    (3, 4, 1),   -- 1× Scrivania in vetro
    (3, 5, 2),   -- 2× Libreria componibile
    -- Sofia (customer 3): 1 recent order
    (4, 2, 2),   -- 2× Sedia ergonomica
    -- Luca (customer 4): 1 recent order
    (5, 1, 1),   -- 1× Tavolo in rovere
    (5, 3, 1),   -- 1× Lampada da terra
    -- Giulia (customer 5): 1 recent order
    (6, 5, 3);   -- 3× Libreria componibile

-- Older-order items (not in the 30-day window)
INSERT INTO order_items (order_id, product_id, quantity) VALUES
    (7,  1, 2),
    (7,  2, 2),
    (8,  4, 1),
    (9,  5, 1);
