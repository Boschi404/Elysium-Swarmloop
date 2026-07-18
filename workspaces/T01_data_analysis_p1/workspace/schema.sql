-- Schema for Sales Report Query Task
-- Assumes a typical e-commerce/product sales database

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT  -- NULL allowed to test 'Uncategorized' handling
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    sale_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
