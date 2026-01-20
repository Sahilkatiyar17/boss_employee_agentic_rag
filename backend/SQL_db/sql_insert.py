import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\company_olap.db")
cursor = conn.cursor()

# -------------------------
# CONSTANTS
# -------------------------
products = [
    ("SmartX Headset", "Audio", "Electronics", "Headset", "SmartX", "One-time"),
    ("SmartX Watch", "Wearable", "Electronics", "Watch", "SmartX", "One-time"),
    ("SmartX Fitness Band", "Wearable", "Electronics", "Band", "SmartX", "Subscription"),
    ("SmartX Earbuds", "Audio", "Electronics", "Earbuds", "SmartX", "One-time"),
    ("SmartX VR Glasses", "VR", "Gaming", "Glasses", "SmartX", "One-time"),
    ("SmartX Smart Glasses", "AR", "Wearable", "Glasses", "SmartX", "Subscription"),
]

regions = ["North India", "South India", "West India", "East India"]
channels = ["Instagram", "Google Ads", "TV", "YouTube", "Website", "Retail"]
departments = ["Sales", "Marketing", "Finance", "Support"]

# -------------------------
# INSERT DIMENSIONS
# -------------------------
cursor.executemany("""
INSERT INTO dim_product(product_name, product_type, category, sub_category, brand, pricing_model)
VALUES (?,?,?,?,?,?)
""", products)

for r in regions:
    cursor.execute("""
    INSERT INTO dim_region(country, state, city, market_region)
    VALUES (?,?,?,?)
    """, ("India", "N/A", "N/A", r))

for ch in channels:
    cursor.execute("INSERT INTO dim_channel VALUES (NULL,?,?)", (ch, "Digital"))

for d in departments:
    cursor.execute("INSERT INTO dim_department VALUES (NULL,?,?)", (d, f"CC_{d}"))

for i in range(1, 21):
    cursor.execute("""
    INSERT INTO dim_employee VALUES (NULL,?,?,?,?)
    """, (f"Employee_{i}", random.choice(["Sales Exec","Manager","Support"]),
          random.choice(departments), random.choice(["Junior","Mid","Senior"])))

for i in range(1, 1001):
    cursor.execute("""
    INSERT INTO dim_customer VALUES (NULL,?,?,?,?,?)
    """, (f"Customer_{i}", random.choice(["New","Returning"]),
          random.choice(["Tech","Retail","Healthcare","Education"]),
          random.choice(["Small","Medium","Large"]),
          random.choice(["Enterprise","SMB","Individual"])))

# -------------------------
# DATE DIMENSION (2 YEARS)
# -------------------------
start = datetime(2024,1,1)
for i in range(730):
    d = start + timedelta(days=i)
    cursor.execute("""
    INSERT INTO dim_date VALUES (NULL,?,?,?,?,?,?,?)
    """, (d.strftime("%Y-%m-%d"), d.day, d.isocalendar()[1],
          d.month, (d.month-1)//3 + 1, d.year, int(d.weekday()>=5)))

conn.commit()

# -------------------------
# FACT SALES (~80k rows)
# -------------------------
cursor.execute("SELECT date_id FROM dim_date")
date_ids = [x[0] for x in cursor.fetchall()]

cursor.execute("SELECT product_id FROM dim_product")
product_ids = [x[0] for x in cursor.fetchall()]

cursor.execute("SELECT customer_id FROM dim_customer")
customer_ids = [x[0] for x in cursor.fetchall()]

cursor.execute("SELECT region_id FROM dim_region")
region_ids = [x[0] for x in cursor.fetchall()]

cursor.execute("SELECT channel_id FROM dim_channel")
channel_ids = [x[0] for x in cursor.fetchall()]

cursor.execute("SELECT employee_id FROM dim_employee")
employee_ids = [x[0] for x in cursor.fetchall()]

sales = []
for _ in range(80000):
    qty = random.randint(1,10)
    price = random.randint(1999, 4999)
    gross = qty * price
    discount = gross * random.uniform(0,0.2)
    tax = gross * 0.18
    net = gross - discount + tax

    sales.append((
        random.choice(date_ids),
        random.choice(product_ids),
        random.choice(customer_ids),
        random.choice(region_ids),
        random.choice(channel_ids),
        random.choice(employee_ids),
        qty, gross, discount, net, tax
    ))

cursor.executemany("""
INSERT INTO fact_sales(
date_id, product_id, customer_id, region_id, channel_id, employee_id,
quantity, gross_amount, discount_amount, net_amount, tax_amount)
VALUES (?,?,?,?,?,?,?,?,?,?,?)
""", sales)

conn.commit()
conn.close()

print("✅ ~80,000 fact_sales rows inserted successfully")
