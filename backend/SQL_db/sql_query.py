import sqlite3

conn = sqlite3.connect(r"F:\sahil\2025-2026\Project_DS\boss-employee-agentic-rag\backend\data\company.db")
cursor = conn.cursor()

query = """
SELECT p.name, c.name, s.quantity, s.sale_date
FROM sales s
JOIN products p ON s.product_id = p.product_id
JOIN customers c ON s.customer_id = c.customer_id
"""

cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    print(row)

query = """
SELECT p.name, SUM(s.quantity) as total_units
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.name
"""

cursor.execute(query)
for row in cursor.fetchall():
    print(row)


conn.close()
