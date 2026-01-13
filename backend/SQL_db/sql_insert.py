import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect(r"F:\sahil\2025-2026\Project_DS\boss-employee-agentic-rag\backend\data\company.db")
cursor = conn.cursor()

# -------------------------
# CONSTANTS
# -------------------------
products = [
    (1, "SmartX Headset", "Headset", 2999, "2023-06-01"),
    (2, "SmartX Watch", "Smartwatch", 4999, "2023-09-15"),
    (3, "SmartX Fitness Band", "Band", 1999, "2024-01-10")
]

regions = ["North India", "South India", "West India", "East India"]
age_groups = ["18-25", "26-35", "36-45", "46-60"]
genders = ["Male", "Female"]
customer_types = ["New", "Returning"]
channels = ["Instagram", "Google Ads", "TV", "YouTube"]

# -------------------------
# INSERT PRODUCTS
# -------------------------
cursor.executemany(
    "INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?)", products
)

# -------------------------
# CUSTOMERS (200)
# -------------------------
customers = []
for cid in range(1, 201):
    customers.append((
        cid,
        random.choice(age_groups),
        random.choice(genders),
        random.choice(regions),
        random.choice(customer_types)
    ))

cursor.executemany(
    "INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?)", customers
)

# -------------------------
# SALES (400)
# -------------------------
sales = []
start_date = datetime(2024, 1, 1)

for sid in range(1, 401):
    product = random.choice(products)
    units = random.randint(1, 10)
    price = product[3]
    revenue = units * price

    sales.append((
        sid,
        product[0],
        (start_date + timedelta(days=random.randint(0, 120))).strftime("%Y-%m-%d"),
        units,
        revenue,
        random.choice(regions)
    ))

cursor.executemany(
    "INSERT OR REPLACE INTO sales VALUES (?, ?, ?, ?, ?, ?)", sales
)

# -------------------------
# MARKETING CAMPAIGNS (10)
# -------------------------
campaigns = []
for cid in range(1, 11):
    product = random.choice(products)
    start = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 30))
    end = start + timedelta(days=30)

    campaigns.append((
        cid,
        product[0],
        random.choice(channels),
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
        random.randint(100000, 500000)
    ))

cursor.executemany(
    "INSERT OR REPLACE INTO marketing_campaigns VALUES (?, ?, ?, ?, ?, ?)", campaigns
)

# -------------------------
# MARKETING PERFORMANCE (120)
# -------------------------
performance = []
pid = 1
for campaign in campaigns:
    for _ in range(12):
        performance.append((
            campaign[0],
            (datetime.strptime(campaign[3], "%Y-%m-%d") +
             timedelta(days=random.randint(1, 28))).strftime("%Y-%m-%d"),
            random.randint(20000, 100000),
            random.randint(1000, 8000),
            random.randint(100, 800)
        ))
        pid += 1

cursor.executemany(
    "INSERT OR REPLACE INTO marketing_performance VALUES (?, ?, ?, ?, ?)", performance
)

# -------------------------
# INVENTORY (30)
# -------------------------
inventory = []
iid = 1
for product in products:
    for region in regions:
        inventory.append((
            product[0],
            region,
            random.randint(100, 1000),
            datetime.now().strftime("%Y-%m-%d")
        ))
        iid += 1

cursor.executemany(
    "INSERT OR REPLACE INTO inventory VALUES (?, ?, ?, ?)", inventory
)

conn.commit()
conn.close()

print("✅ Large-scale SQL dataset generated successfully")
