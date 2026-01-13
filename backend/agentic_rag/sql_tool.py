import sqlite3

DB_PATH = r"F:\sahil\2025-2026\Project_DS\boss-employee-agentic-rag\backend\data\company.db"

def build_sql_from_intent(intent: dict):
    base_query = """
    SELECT p.product_name, s.region, SUM(s.units_sold), SUM(s.revenue)
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    WHERE 1=1
    """

    params = []

    filters = intent.get("filters", {})

    if "region" in filters:
        base_query += " AND s.region = ?"
        params.append(filters["region"])

    if "category" in filters:
        base_query += " AND p.category = ?"
        params.append(filters["category"])

    base_query += " GROUP BY p.product_name, s.region"

    return base_query, params


def run_sql(intent: dict) -> str:
    query, params = build_sql_from_intent(intent)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)

    rows = cursor.fetchall()
    conn.close()

    return str(rows)

# Dummy intent similar to what your JsonOutputParser produces
from sql_tool import run_sql

fake_sql_intent = {
    "filters": {
        "region": "South India"
    }
}

print(run_sql(fake_sql_intent))
