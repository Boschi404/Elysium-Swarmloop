-- ============================================================
-- Sales Report: Total Sales by Product Category (Q4 2024)
-- Columns: category_name, total_units_sold, total_revenue,
--          avg_price
-- Sort:   revenue descending
-- Notes:  NULL categories → 'Uncategorized'
--         Amounts rounded to 2 decimal places
-- ============================================================

SELECT
    COALESCE(p.category, 'Uncategorized') AS category_name,
    COUNT(s.sale_id)                       AS total_units_sold,
    ROUND(SUM(s.amount), 2)                AS total_revenue,
    ROUND(AVG(s.amount), 2)                AS avg_price
FROM sales s
JOIN products p ON s.product_id = p.product_id
WHERE s.sale_date >= '2024-10-01'
  AND s.sale_date <  '2025-01-01'
GROUP BY COALESCE(p.category, 'Uncategorized')
ORDER BY total_revenue DESC;
