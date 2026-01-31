import sqlite3

DB_PATH = r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\analytics_flat.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales_flat_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Date
    full_date TEXT,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    is_weekend INTEGER,

    -- Product
    product_name TEXT,
    category TEXT,
    sub_category TEXT,
    brand TEXT,

    -- Region
    market_region TEXT,
    country TEXT,
    state TEXT,

    -- Channel
    channel_name TEXT,

    -- Employee (aggregated business lens)
    department TEXT,

    -- Metrics
    quantity INTEGER,
    gross_amount REAL,
    discount_amount REAL,
    net_amount REAL,
    tax_amount REAL,
    profit_estimate REAL
);
""")

conn.commit()
conn.close()

print("✅ Table created")
