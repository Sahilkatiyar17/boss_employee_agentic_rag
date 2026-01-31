import sqlite3
import pandas as pd
import os

DB_PATH = r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\analytics_flat.db"
EXPORT_FOLDER = r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\output_sql"

os.makedirs(EXPORT_FOLDER, exist_ok=True)

ALLOWED_COLUMNS = [
    "full_date","year","month","quarter","is_weekend",
    "product_name","category","sub_category","brand",
    "market_region","country","state",
    "channel_name","department",
    "quantity","gross_amount","discount_amount",
    "net_amount","tax_amount","profit_estimate"
]

# -------------------------
# SIMPLE CSV NAME HANDLER
# -------------------------
def get_next_csv_path(base_name="query_output.csv"):
    base_path = os.path.join(EXPORT_FOLDER, base_name)

    if not os.path.exists(base_path):
        return base_path

    name, ext = os.path.splitext(base_name)
    counter = 1

    while True:
        new_name = f"{name}({counter}){ext}"
        new_path = os.path.join(EXPORT_FOLDER, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1


# -------------------------
# BUILD SQL FROM INTENT
# -------------------------
def build_sql_from_intent(intent: dict):
    select = intent.get("select", ["*"])
    filters = intent.get("filters", {})
    group_by = intent.get("group_by", [])

    # Validate SELECT columns
    if "*" not in select:
        select = [col for col in select if col in ALLOWED_COLUMNS]
        if not select:
            select = ["*"]
    else:
        select = ["*"]

    select_clause = ", ".join(select)

    sql = f"SELECT {select_clause} FROM sales_flat_analytics"
    params = []

    # WHERE clause
    where = []

    for col, value in filters.items():

        # Special handling: date range
        if col == "full_date_between" and isinstance(value, list) and len(value) == 2:
            where.append("full_date BETWEEN ? AND ?")
            params.extend(value)

        # Normal filters
        elif col in ALLOWED_COLUMNS:
            if isinstance(value, list):
                where.append(f"{col} BETWEEN ? AND ?")
                params.extend(value)
            else:
                where.append(f"{col} = ?")
                params.append(value)

    if where:
        sql += " WHERE " + " AND ".join(where)

    # GROUP BY
    if group_by:
        valid_group = [g for g in group_by if g in ALLOWED_COLUMNS]
        if valid_group:
            sql += " GROUP BY " + ", ".join(valid_group)

    return sql, params


# -------------------------
# RUN INTENT QUERY → CSV
# -------------------------
def run_intent_query(intent: dict):
    try:
        sql, params = build_sql_from_intent(intent)

        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn, params=params)
        conn.close()

        # Generate simple filename
        file_path = get_next_csv_path("query_output.csv")

        df.to_csv(file_path, index=False)

        return file_path  # ✅ RETURN ONLY CSV PATH

    except Exception as e:
        print("⚠️ SQL failed, running fallback:", e)

        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * FROM sales_flat_analytics LIMIT 1000", conn)
            conn.close()

            file_path = get_next_csv_path("fallback_output.csv")
            df.to_csv(file_path, index=False)

            return file_path

        except:
            return None

def run_sql(intent: dict):
    
    print("The dataset extracted and saved at: ", "F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\output_sql")
    return run_intent_query(intent)
# -------------------------
# TEST INTENT
# -------------------------
#intent =   {'select': ['*'], 'filters': {'month': '4','year':'2023','product_name':'SmartX Watch'}, 'group_by': [], 'metrics': [], 'aggregation': None, 'limit': 1000}
#print("CSV Path:", run_intent_query(intent))
