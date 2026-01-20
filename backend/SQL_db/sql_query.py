import sqlite3

conn = sqlite3.connect(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\company_olap.db")
cursor = conn.cursor()

# Total Revenue
cursor.execute("""
SELECT SUM(net_amount) FROM fact_sales
""")
print("Total Revenue:", cursor.fetchone()[0])

# Revenue by Product
cursor.execute("""
SELECT p.product_name, SUM(f.net_amount)
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY 2 DESC
""")

print("\nRevenue by Product:")
for row in cursor.fetchall():
    print(row)

conn.close()
