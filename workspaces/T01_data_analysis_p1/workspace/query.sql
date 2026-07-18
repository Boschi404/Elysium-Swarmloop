-- ============================================================================
-- Sales Report Query — Total Sales by Product Category for Q4 2024
-- ============================================================================
-- Requirements:
--   - Total units sold, total revenue, average price per category
--   - NULL categories → 'Uncategorized'
--   - Sort by revenue descending
--   - Rounded to 2 decimal places
-- ============================================================================

SELECT
    COALESCE(p.category, 'Uncategorized')                       AS category_name,
    SUM(s.quantity)                                              AS total_units_sold,
    ROUND(SUM(s.quantity * s.price), 2)                          AS total_revenue,
    ROUND(AVG(s.price), 2)                                       AS average_price
FROM sales s
JOIN products p ON s.product_id = p.id
WHERE s.sale_date >= '2024-10-01'
  AND s.sale_date <  '2025-01-01'
GROUP BY p.category
ORDER BY total_revenue DESC;
