-- Seed data for testing the Sales Report Query
-- Includes edge cases: NULL category, multiple products per category, Q3 vs Q4 boundary

INSERT INTO products (id, name, category) VALUES
    (1,  'Wireless Mouse',       'Electronics'),
    (2,  'USB-C Hub',            'Electronics'),
    (3,  'Desk Lamp',            'Home Office'),
    (4,  'Ergonomic Chair',      'Home Office'),
    (5,  'Notebook Set',         'Stationery'),
    (6,  'Ballpoint Pens (12pk)','Stationery'),
    (7,  'Standing Desk',        'Home Office'),
    (8,  'Webcam HD',            'Electronics'),
    (9,  'Generic Widget',       NULL),            -- NULL category → 'Uncategorized'
    (10, 'Misc Part',            NULL);            -- NULL category → 'Uncategorized'

INSERT INTO sales (id, product_id, quantity, price, sale_date) VALUES
    -- Q4 2024 sales (target period)
    (1,  1,  3,  25.99,  '2024-10-05'),
    (2,  1,  1,  24.50,  '2024-11-12'),
    (3,  2,  5,  18.75,  '2024-10-20'),
    (4,  3,  2,  45.00,  '2024-10-15'),
    (5,  4,  1, 299.99,  '2024-11-01'),
    (6,  4,  1, 289.99,  '2024-12-10'),
    (7,  5, 10,   8.50,  '2024-10-30'),
    (8,  6,  4,   6.99,  '2024-11-05'),
    (9,  7,  1, 449.00,  '2024-12-01'),
    (10, 8,  2,  79.99,  '2024-11-20'),
    (11, 9,  7,  12.50,  '2024-10-10'),
    (12, 10, 3,   5.00,  '2024-12-05'),
    -- Sales outside Q4 2024 (should be excluded)
    (13, 1,  2,  22.00,  '2024-09-30'),   -- Q3 2024
    (14, 3,  1,  42.00,  '2024-07-15'),   -- Q3 2024
    (15, 5,  5,   9.00,  '2025-01-10'),   -- Q1 2025
    (16, 8,  1,  69.99,  '2024-06-01');   -- Q2 2024
