import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\analytics_flat.db"

products = [
    ("SmartX Watch", "Electronics", "Wearable", "SmartX"),
    ("Vision AR Glasses", "Electronics", "AR/VR", "VisionTech"),
    ("Power Laptop", "Computers", "Laptop", "VoltPC"),
    ("FitBand Pro", "Electronics", "Wearable", "FitBand"),
    ("HomeHub Speaker", "Electronics", "Smart Home", "HomeHub"),
]

regions = [
    ("North India", "India", "Delhi"),
    ("West India", "India", "Maharashtra"),
    ("South India", "India", "Karnataka"),
    ("East India", "India", "West Bengal")
]

channels = ["Retail", "Website", "Instagram", "Enterprise"]
departments = ["Sales", "Marketing", "Partnerships"]

start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)

# 🎯 Reduced target rows
rows_to_insert = 100_000

def seasonal_multiplier(month):
    if month in [10, 11]: return 1.5   # festive boost
    if month in [6, 7]: return 1.2     # summer bump
    return 1.0

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

batch = []

for i in range(rows_to_insert):
    date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    year = date.year
    month = date.month
    quarter = (month - 1) // 3 + 1
    is_weekend = 1 if date.weekday() >= 5 else 0

    product = random.choice(products)
    region = random.choice(regions)
    channel = random.choice(channels)
    department = random.choice(departments)

    base_qty = random.randint(1, 6)  # smaller base = fewer rows impact
    season = seasonal_multiplier(month)
    weekend_boost = 1.15 if is_weekend else 1.0

    quantity = max(1, int(base_qty * season * weekend_boost))

    price = random.randint(4000, 75000)
    gross = quantity * price

    discount = gross * random.uniform(0.05, 0.22)
    net = gross - discount
    tax = net * 0.18
    profit = net * random.uniform(0.12, 0.32)

    batch.append((
        date.strftime("%Y-%m-%d"),
        year, month, quarter, is_weekend,
        product[0], product[1], product[2], product[3],
        region[0], region[1], region[2],
        channel, department,
        quantity, gross, discount, net, tax, profit
    ))

    if len(batch) == 5000:
        cursor.executemany("""
        INSERT INTO sales_flat_analytics (
            full_date,
            year, month, quarter, is_weekend,
            product_name, category, sub_category, brand,
            market_region, country, state,
            channel_name, department,
            quantity, gross_amount, discount_amount,
            net_amount, tax_amount, profit_estimate
        ) VALUES (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )
        """, batch)

        conn.commit()
        batch.clear()

# Insert leftovers
if batch:
    cursor.executemany("""
    INSERT INTO sales_flat_analytics VALUES (
        NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
    )
    """, batch)
    conn.commit()

conn.close()
print("✅ 100K rows inserted successfully")
