-- ============================================================
-- E-commerce Dashboard — Database Initialization
-- ============================================================
-- This file is auto-executed by Postgres on first container start
-- via the docker-compose volume mount below.
-- ============================================================

CREATE TABLE IF NOT EXISTS orders (
    id               SERIAL PRIMARY KEY,
    product          VARCHAR(100)   NOT NULL,
    product_category VARCHAR(50)    NOT NULL,
    region           VARCHAR(50)    NOT NULL,
    price            NUMERIC(10,2)  NOT NULL CHECK (price > 0),
    quantity         INTEGER        NOT NULL DEFAULT 1 CHECK (quantity > 0),
    status           VARCHAR(20)    NOT NULL DEFAULT 'delivered'
                         CHECK (status IN ('pending', 'shipped', 'delivered', 'cancelled')),
    order_time       TIMESTAMP      NOT NULL DEFAULT NOW()
);

-- Index for time-series queries (sales-over-time endpoint)
CREATE INDEX IF NOT EXISTS idx_orders_order_time
    ON orders (order_time);

-- Index for grouped metric queries
CREATE INDEX IF NOT EXISTS idx_orders_category
    ON orders (product_category);

CREATE INDEX IF NOT EXISTS idx_orders_region
    ON orders (region);

-- ============================================================
-- Seed Data — 200 realistic Indian e-commerce orders
-- spread across 90 days, 5 categories, 4 regions
-- ============================================================

INSERT INTO orders (product, product_category, region, price, quantity, status, order_time)
SELECT
    product,
    category,
    region,
    price,
    quantity,
    status,
    NOW() - (random() * INTERVAL '90 days')
FROM (VALUES
    ('iPhone 15',           'Electronics', 'North', 79999, 1, 'delivered'),
    ('Samsung Galaxy S24',  'Electronics', 'South', 74999, 1, 'delivered'),
    ('OnePlus 12',          'Electronics', 'East',  59999, 1, 'shipped'),
    ('MacBook Air M2',      'Electronics', 'West',  114999,1, 'delivered'),
    ('Dell XPS 15',         'Electronics', 'North', 129999,1, 'delivered'),
    ('Sony WH-1000XM5',     'Electronics', 'South', 24999, 1, 'delivered'),
    ('iPad Air',            'Electronics', 'East',  59999, 1, 'pending'),
    ('Realme GT 5',         'Electronics', 'West',  29999, 2, 'delivered'),
    ('Boat Rockerz 450',    'Electronics', 'North', 1499,  3, 'delivered'),
    ('Mi Smart TV 43"',     'Electronics', 'South', 27999, 1, 'shipped'),
    ('Canon EOS R50',       'Electronics', 'East',  64999, 1, 'delivered'),
    ('Noise ColorFit Pro',  'Electronics', 'West',  2499,  2, 'delivered'),
    ('Logitech MX Master',  'Electronics', 'North', 8999,  1, 'delivered'),
    ('Asus ROG Phone 7',    'Electronics', 'South', 69999, 1, 'cancelled'),
    ('JBL Flip 6',          'Electronics', 'East',  9999,  2, 'delivered'),

    ('Levi''s 512 Jeans',   'Fashion',     'North', 3999,  2, 'delivered'),
    ('Nike Air Max 270',    'Fashion',     'South', 9995,  1, 'delivered'),
    ('Adidas Ultraboost',   'Fashion',     'East',  14999, 1, 'shipped'),
    ('Zara Floral Dress',   'Fashion',     'West',  3490,  1, 'delivered'),
    ('H&M Formal Shirt',    'Fashion',     'North', 1299,  3, 'delivered'),
    ('Puma Sports Shorts',  'Fashion',     'South', 899,   4, 'delivered'),
    ('Woodland Boots',      'Fashion',     'East',  4999,  1, 'pending'),
    ('Raymond Suit',        'Fashion',     'West',  12999, 1, 'delivered'),
    ('Fastrack Watch',      'Fashion',     'North', 2295,  2, 'delivered'),
    ('Titan Raga',          'Fashion',     'South', 8995,  1, 'delivered'),
    ('Allen Solly Chinos',  'Fashion',     'East',  2499,  2, 'shipped'),
    ('Lavie Handbag',       'Fashion',     'West',  1999,  1, 'delivered'),
    ('Bata Loafers',        'Fashion',     'North', 1799,  1, 'delivered'),
    ('Van Heusen Blazer',   'Fashion',     'South', 6999,  1, 'delivered'),
    ('UCB Denim Jacket',    'Fashion',     'East',  5499,  1, 'cancelled'),

    ('Prestige Cooker 5L',  'Home',        'North', 1899,  1, 'delivered'),
    ('Philips Air Fryer',   'Home',        'South', 5999,  1, 'delivered'),
    ('Dyson V15 Vacuum',    'Home',        'East',  49900, 1, 'delivered'),
    ('Milton Casserole Set','Home',        'West',  799,   2, 'delivered'),
    ('Godrej Refrigerator', 'Home',        'North', 34999, 1, 'shipped'),
    ('Bajaj Mixer Grinder', 'Home',        'South', 2799,  1, 'delivered'),
    ('Havells Iron',        'Home',        'East',  1499,  2, 'delivered'),
    ('Usha Ceiling Fan',    'Home',        'West',  2499,  2, 'delivered'),
    ('Cello Steel Bottle',  'Home',        'North', 499,   5, 'delivered'),
    ('Nestaway Bedsheet',   'Home',        'South', 999,   3, 'delivered'),
    ('IKEA Study Lamp',     'Home',        'East',  1499,  1, 'pending'),
    ('Solimo Pillow Set',   'Home',        'West',  699,   4, 'delivered'),
    ('Borosil Glass Set',   'Home',        'North', 899,   2, 'delivered'),
    ('WD My Passport 1TB',  'Home',        'South', 4299,  1, 'delivered'),
    ('Whirlpool Washer',    'Home',        'East',  28999, 1, 'shipped'),

    ('Atomic Habits',       'Books',       'North', 399,   2, 'delivered'),
    ('Rich Dad Poor Dad',   'Books',       'South', 299,   3, 'delivered'),
    ('The Alchemist',       'Books',       'East',  199,   4, 'delivered'),
    ('Zero to One',         'Books',       'West',  499,   2, 'delivered'),
    ('Deep Work',           'Books',       'North', 449,   2, 'delivered'),
    ('Ikigai',              'Books',       'South', 299,   5, 'delivered'),
    ('Sapiens',             'Books',       'East',  599,   1, 'delivered'),
    ('1984 - Orwell',       'Books',       'West',  199,   3, 'delivered'),
    ('Think & Grow Rich',   'Books',       'North', 249,   4, 'shipped'),
    ('The Psychology of $', 'Books',       'South', 349,   3, 'delivered'),
    ('Clean Code',          'Books',       'East',  999,   1, 'delivered'),
    ('Designing Data Apps', 'Books',       'West',  1299,  1, 'delivered'),
    ('Harry Potter Box Set','Books',       'North', 2499,  1, 'delivered'),
    ('Wings of Fire',       'Books',       'South', 299,   6, 'delivered'),
    ('The Lean Startup',    'Books',       'East',  499,   2, 'cancelled'),

    ('Aashirvaad Atta 5kg', 'Grocery',    'North', 299,   4, 'delivered'),
    ('Amul Butter 500g',    'Grocery',    'South', 275,   6, 'delivered'),
    ('Tata Tea Gold 500g',  'Grocery',    'East',  299,   5, 'delivered'),
    ('Fortune Sunflower Oil','Grocery',   'West',  189,   8, 'delivered'),
    ('Maggi Noodles 12pk',  'Grocery',    'North', 192,   10,'delivered'),
    ('Parle-G Biscuits',    'Grocery',    'South', 65,    20, 'delivered'),
    ('Dettol Handwash',     'Grocery',    'East',  149,   6, 'delivered'),
    ('Ariel Detergent 3kg', 'Grocery',    'West',  649,   3, 'delivered'),
    ('Vim Dishwash Bar',    'Grocery',    'North', 99,    10, 'delivered'),
    ('Colgate MaxFresh',    'Grocery',    'South', 129,   8, 'shipped'),
    ('Everest Garam Masala','Grocery',    'East',  99,    6, 'delivered'),
    ('Saffola Oats 1kg',    'Grocery',    'West',  239,   5, 'delivered'),
    ('Dabur Honey 500g',    'Grocery',    'North', 249,   4, 'delivered'),
    ('Nestlé KitKat 8pk',   'Grocery',    'South', 199,   8, 'delivered'),
    ('Real Fruit Juice 1L', 'Grocery',    'East',  129,   10,'delivered')
) AS t(product, category, region, price, quantity, status);

-- Multiply rows ~20x with randomised dates
-- GREATEST(..., 1) ensures price never goes below 1
INSERT INTO orders (product, product_category, region, price, quantity, status, order_time)
SELECT
    product,
    product_category,
    region,
    GREATEST(price + (random() * 200 - 50)::NUMERIC(10,2), 1),
    quantity,
    CASE
        WHEN random() < 0.05 THEN 'cancelled'
        WHEN random() < 0.15 THEN 'pending'
        WHEN random() < 0.30 THEN 'shipped'
        ELSE 'delivered'
    END,
    NOW() - (random() * INTERVAL '90 days')
FROM orders, generate_series(1, 20);