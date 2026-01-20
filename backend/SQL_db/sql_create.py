import sqlite3

# -------------------------
# SQLITE CONNECTION
# -------------------------
conn = sqlite3.connect(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\company_olap.db")
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON;")

# -------------------------
# DROP TABLES (Clean slate)
# -------------------------
tables = [
    "fact_sales",
    "fact_service_usage",
    "fact_finance_snapshot",
    "dim_product",
    "dim_customer",
    "dim_date",
    "dim_region",
    "dim_channel",
    "dim_employee",
    "dim_department"
]

for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table}")

# -------------------------
# DIMENSION TABLES
# -------------------------
cursor.execute("""
CREATE TABLE dim_product (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    product_type TEXT,
    category TEXT,
    sub_category TEXT,
    brand TEXT,
    pricing_model TEXT
);
""")

cursor.execute("""
CREATE TABLE dim_customer (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    customer_type TEXT,
    industry TEXT,
    company_size TEXT,
    customer_segment TEXT
);
""")

cursor.execute("""
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_date TEXT,
    day INTEGER,
    week INTEGER,
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    is_weekend INTEGER
);
""")

cursor.execute("""
CREATE TABLE dim_region (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT,
    state TEXT,
    city TEXT,
    market_region TEXT
);
""")

cursor.execute("""
CREATE TABLE dim_channel (
    channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_name TEXT,
    channel_type TEXT
);
""")

cursor.execute("""
CREATE TABLE dim_employee (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT,
    role TEXT,
    department TEXT,
    experience_level TEXT
);
""")

cursor.execute("""
CREATE TABLE dim_department (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT,
    cost_center TEXT
);
""")

# -------------------------
# FACT TABLES
# -------------------------
cursor.execute("""
CREATE TABLE fact_sales (
    sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id INTEGER,
    product_id INTEGER,
    customer_id INTEGER,
    region_id INTEGER,
    channel_id INTEGER,
    employee_id INTEGER,
    quantity INTEGER,
    gross_amount REAL,
    discount_amount REAL,
    net_amount REAL,
    tax_amount REAL,
    FOREIGN KEY(date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY(product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY(customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY(region_id) REFERENCES dim_region(region_id),
    FOREIGN KEY(channel_id) REFERENCES dim_channel(channel_id),
    FOREIGN KEY(employee_id) REFERENCES dim_employee(employee_id)
);
""")

cursor.execute("""
CREATE TABLE fact_service_usage (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id INTEGER,
    service_id INTEGER,
    customer_id INTEGER,
    region_id INTEGER,
    usage_count INTEGER,
    duration_minutes REAL,
    cost_incurred REAL
);
""")

cursor.execute("""
CREATE TABLE fact_finance_snapshot (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id INTEGER,
    department_id INTEGER,
    total_revenue REAL,
    total_cost REAL,
    profit REAL,
    operational_expense REAL
);
""")

conn.commit()
conn.close()

print("✅ SQLite OLAP schema created successfully")
