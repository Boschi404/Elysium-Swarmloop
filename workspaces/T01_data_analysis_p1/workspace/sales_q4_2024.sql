/*
 * T01_data_analysis — SQL: Sales Report Query
 * =============================================
 * Returns total sales by product category for Q4 2024.
 * Columns: category_name, total_units_sold, total_revenue, avg_price
 * Sorted by revenue descending. NULL categories → 'Uncategorized'.
 * Amounts rounded to 2 decimal places.
 *
 * Assumes a relational schema with:
 *   - sales(id, product_id, units, unit_price, sale_date)
 *   - products(id, name, category_id)
 *   - categories(id, name)
 */

SELECT
    COALESCE(c.name, 'Uncategorized')           AS category_name,
    SUM(s.units)                                 AS total_units_sold,
    ROUND(SUM(s.units * s.unit_price), 2)        AS total_revenue,
    ROUND(AVG(s.unit_price), 2)                  AS avg_price
FROM sales s
JOIN products p ON s.product_id = p.id
LEFT JOIN categories c ON p.category_id = c.id
WHERE s.sale_date BETWEEN '2024-10-01' AND '2024-12-31'
GROUP BY c.name
ORDER BY total_revenue DESC;
