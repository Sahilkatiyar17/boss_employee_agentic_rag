import sqlite3
from typing import Dict, List, Tuple

DB_PATH = r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\company_olap.db"


# -------------------------
# SCHEMA METADATA (CRITICAL)
# -------------------------

FACT_TABLES = {
    "fact_sales": {
        "table": "fact_sales",
        "joins": {
            "dim_product": ("product_id", "product_id"),
            "dim_date": ("date_id", "date_id"),
            "dim_region": ("region_id", "region_id"),
            "dim_channel": ("channel_id", "channel_id"),
            "dim_employee": ("employee_id", "employee_id"),
        },
        "metrics": {
            "quantity": "SUM(f.quantity)",
            "gross_amount": "SUM(f.gross_amount)",
            "discount_amount": "SUM(f.discount_amount)",
            "net_amount": "SUM(f.net_amount)",
            "tax_amount": "SUM(f.tax_amount)"
        }
    },

    "fact_service_usage": {
        "table": "fact_service_usage",
        "joins": {
            "dim_product": ("service_id", "product_id"),
            "dim_date": ("date_id", "date_id"),
            "dim_region": ("region_id", "region_id"),
            "dim_customer": ("customer_id", "customer_id")
        },
        "metrics": {
            "usage_count": "SUM(f.usage_count)",
            "duration_minutes": "SUM(f.duration_minutes)",
            "cost_incurred": "SUM(f.cost_incurred)"
        }
    },

    "fact_finance_snapshot": {
        "table": "fact_finance_snapshot",
        "joins": {
            "dim_date": ("date_id", "date_id"),
            "dim_department": ("department_id", "department_id")
        },
        "metrics": {
            "total_revenue": "SUM(f.total_revenue)",
            "total_cost": "SUM(f.total_cost)",
            "profit": "SUM(f.profit)",
            "operational_expense": "SUM(f.operational_expense)"
        }
    }
}


DIMENSION_COLUMNS = {
    "product_name": ("dim_product", "product_name"),
    "product_type": ("dim_product", "product_type"),
    "category": ("dim_product", "category"),
    "sub_category": ("dim_product", "sub_category"),

    "customer_type": ("dim_customer", "customer_type"),
    "industry": ("dim_customer", "industry"),
    "customer_segment": ("dim_customer", "customer_segment"),

    "market_region": ("dim_region", "market_region"),
    "country": ("dim_region", "country"),
    "state": ("dim_region", "state"),
    "city": ("dim_region", "city"),

    "channel_name": ("dim_channel", "channel_name"),
    "role": ("dim_employee", "role"),
    "department": ("dim_employee", "department"),

    "year": ("dim_date", "year"),
    "quarter": ("dim_date", "quarter"),
    "month": ("dim_date", "month"),
    "full_date": ("dim_date", "full_date"),
}


# -------------------------
# SQL BUILDER
# -------------------------

def build_sql_from_intent(intent: Dict) -> Tuple[str, List]:
    fact_name = intent["tables"][0]
    metrics = intent.get("metrics", [])
    dimensions = intent.get("dimensions", [])
    filters = intent.get("filters", {})

    fact = FACT_TABLES[fact_name]
    params = []

    select_clauses = []
    group_by_clauses = []
    join_clauses = []

    # Metrics
    for metric in metrics:
        select_clauses.append(fact["metrics"][metric] + f" AS {metric}")

    # Dimensions
    used_dimensions = set()
    for dim in dimensions:
        dim_table, dim_col = DIMENSION_COLUMNS[dim]
        select_clauses.append(f"{dim_table}.{dim_col} AS {dim}")
        group_by_clauses.append(f"{dim_table}.{dim_col}")
        used_dimensions.add(dim_table)

    # Joins
    for dim_table, (fact_key, dim_key) in fact["joins"].items():
        if dim_table in used_dimensions or any(
            DIMENSION_COLUMNS.get(f, [None])[0] == dim_table for f in filters
        ):
            join_clauses.append(
                f"LEFT JOIN {dim_table} ON f.{fact_key} = {dim_table}.{dim_key}"
            )

    # WHERE
    where_clauses = []
    for field, value in filters.items():
        dim_table, dim_col = DIMENSION_COLUMNS[field]
        where_clauses.append(f"{dim_table}.{dim_col} = ?")
        params.append(value)

    # Assemble SQL
    sql = f"""
    SELECT
        {", ".join(select_clauses)}
    FROM {fact['table']} f
    {' '.join(join_clauses)}
    """

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    if group_by_clauses:
        sql += " GROUP BY " + ", ".join(group_by_clauses)

    return sql.strip(), params


# -------------------------
# RUNNER
# -------------------------

def run_sql(intent: Dict) -> str:
    query, params = build_sql_from_intent(intent)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return str(rows)

fake_intent_2 = {
    "fact": "fact_sales",
    "metrics": ["net_amount"],
    "dimensions": ["month", "year"],
    "filters": {
        "product_name": "SmartX Watch"
    }
}

#print(run_sql(fake_intent_2))