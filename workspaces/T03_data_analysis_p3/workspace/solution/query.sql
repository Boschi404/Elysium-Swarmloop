-- =============================================================================
-- T03_data_analysis_p3 — Multi-Table JOIN Report
-- =============================================================================
-- Returns: customer name, order date, product name, quantity, line total
-- Filter: orders from the last 30 days
-- Include: customers with NO orders (0 quantity, NULL product)
-- Sort:   order date DESC, customer name ASC
-- =============================================================================

SELECT
    c.customer_name,
    o.order_date,
    p.product_name,
    COALESCE(oi.quantity, 0)                       AS quantity,
    COALESCE(oi.quantity * p.price, 0.0)            AS line_total
FROM customers c
LEFT JOIN orders o
    ON  c.customer_id = o.customer_id
    AND o.order_date >= DATE('now', '-30 days')
LEFT JOIN order_items oi
    ON  o.order_id = oi.order_id
LEFT JOIN products p
    ON  oi.product_id = p.product_id
ORDER BY
    o.order_date DESC,      -- recent first; NULL (no-order customers) last
    c.customer_name ASC;
