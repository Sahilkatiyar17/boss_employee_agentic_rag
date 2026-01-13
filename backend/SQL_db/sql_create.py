import sqlite3

conn = sqlite3.connect(r"F:\sahil\2025-2026\Project_DS\boss-employee-agentic-rag\backend\data\company.db")
cursor = conn.cursor()

# PRODUCTS
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price REAL,
    launch_date TEXT
)
""")

# SALES
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY,
    product_id INTEGER,
    sale_date TEXT,
    units_sold INTEGER,
    revenue REAL,
    region TEXT,
    FOREIGN KEY(product_id) REFERENCES products(product_id)
)
""")

# CUSTOMERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    age_group TEXT,
    gender TEXT,
    region TEXT,
    customer_type TEXT
)
""")

# MARKETING CAMPAIGNS
cursor.execute("""
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    campaign_id INTEGER PRIMARY KEY,
    product_id INTEGER,
    channel TEXT,
    start_date TEXT,
    end_date TEXT,
    budget REAL,
    FOREIGN KEY(product_id) REFERENCES products(product_id)
)
""")

# MARKETING PERFORMANCE
cursor.execute("""
CREATE TABLE IF NOT EXISTS marketing_performance (
    campaign_id INTEGER,
    date TEXT,
    impressions INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    FOREIGN KEY(campaign_id) REFERENCES marketing_campaigns(campaign_id)
)
""")

# INVENTORY
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    product_id INTEGER,
    warehouse_region TEXT,
    stock_available INTEGER,
    last_updated TEXT,
    FOREIGN KEY(product_id) REFERENCES products(product_id)
)
""")

conn.commit()
conn.close()

print("✅ SQL schema created successfully")
