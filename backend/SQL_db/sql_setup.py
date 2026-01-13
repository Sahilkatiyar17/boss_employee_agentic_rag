import sqlite3
from datetime import datetime
conn = sqlite3.connect(r"F:\sahil\2025-2026\Project_DS\boss-employee-agentic-rag\backend\data\company.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    launch_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    region TEXT,
    signup_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    customer_id INTEGER,
    quantity INTEGER,
    sale_date TEXT,
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
)
""")

products = [
    ("SmartX Headset", "Headset", 2999.0, "2024-01-10"),
    ("SmartX Earbuds", "Earbuds", 1999.0, "2024-03-15"),
    ("SmartX Watch", "Wearable", 4999.0, "2023-11-20")
]

cursor.executemany("""
INSERT INTO products (name, category, price, launch_date)
VALUES (?, ?, ?, ?)
""", products)

customers = [
    ("Amit Sharma", "North India", "2024-02-01"),
    ("Priya Verma", "South India", "2024-02-10"),
    ("Rohan Das", "East India", "2024-03-05")
]

cursor.executemany("""
INSERT INTO customers (name, region, signup_date)
VALUES (?, ?, ?)
""", customers)

sales = [
    (1, 1, 2, "2024-04-01"),
    (2, 2, 1, "2024-04-02"),
    (3, 3, 1, "2024-04-03"),
    (1, 2, 1, "2024-04-04")
]

cursor.executemany("""
INSERT INTO sales (product_id, customer_id, quantity, sale_date)
VALUES (?, ?, ?, ?)
""", sales)

conn.commit()
conn.close()

print("Database setup completed successfully.")
