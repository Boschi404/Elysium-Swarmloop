/*
 * T01_data_analysis - Sales Report Query
 * Returns total sales by product category for Q4 2024.
 *
 * Schema assumptions:
 *   sales(sale_id, product_id, quantity, unit_price, sale_date)
 *   products(product_id, product_name, category_id)
 *   categories(category_id, category_name)
 *
 * Requirements:
 *   - category name, total units sold, total revenue, average price
 *   - NULL categories shown as 'Uncategorized'
 *   - amounts rounded to 2 decimals
 *   - sorted by revenue descending
 */

SELECT
    COALESCE(c.category_name, 'Uncategorized') AS category_name,
    SUM(s.quantity) AS total_units_sold,
    ROUND(SUM(s.quantity * s.unit_price), 2) AS total_revenue,
    ROUND(SUM(s.quantity * s.unit_price) / NULLIF(SUM(s.quantity), 0), 2) AS average_price
FROM sales s
LEFT JOIN products p ON s.product_id = p.product_id
LEFT JOIN categories c ON p.category_id = c.category_id
WHERE s.sale_date >= '2024-10-01'
  AND s.sale_date < '2025-01-01'
GROUP BY c.category_name
ORDER BY total_revenue DESC;
