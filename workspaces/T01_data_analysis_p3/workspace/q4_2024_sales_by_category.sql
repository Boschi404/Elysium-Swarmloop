-- ============================================================
-- T01_data_analysis: SQL Sales Report Query
-- Total sales by product category for Q4 2024
-- Includes: category name, total units sold, total revenue,
--           average price. Sorted by revenue descending.
-- NULL categories handled as 'Uncategorized'.
-- Amounts rounded to 2 decimals.
-- ============================================================

-- Assumed schema:
--   sales(id, product_id, quantity, unit_price, sale_date)
--   products(id, name, category_id)
--   categories(id, name)

SELECT
    COALESCE(c.name, 'Uncategorized') AS category_name,
    SUM(s.quantity)                   AS total_units_sold,
    ROUND(SUM(s.quantity * s.unit_price), 2) AS total_revenue,
    ROUND(AVG(s.unit_price), 2)       AS average_price
FROM sales s
JOIN products p ON s.product_id = p.id
LEFT JOIN categories c ON p.category_id = c.id
WHERE s.sale_date >= '2024-10-01'
  AND s.sale_date <  '2025-01-01'
GROUP BY c.name
ORDER BY total_revenue DESC;
