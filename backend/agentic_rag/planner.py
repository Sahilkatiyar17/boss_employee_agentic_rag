
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
llm=ChatGroq(model_name="openai/gpt-oss-120b")
llm



planner_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """
You are a retrieval planner for an Agentic RAG system.

You have access to:
You have access to:
1. SQL Database (

FACT_TABLES = {{
    "fact_sales": {{
        "table": "fact_sales",
        "joins": {{
            "dim_product": ("product_id", "product_id"),
            "dim_date": ("date_id", "date_id"),
            "dim_region": ("region_id", "region_id"),
            "dim_channel": ("channel_id", "channel_id"),
            "dim_employee": ("employee_id", "employee_id")
        }},
        "metrics": {{
            "quantity": "SUM(f.quantity)",
            "gross_amount": "SUM(f.gross_amount)",
            "discount_amount": "SUM(f.discount_amount)",
            "net_amount": "SUM(f.net_amount)",
            "tax_amount": "SUM(f.tax_amount)"
        }}
    }},

    "fact_service_usage": {{
        "table": "fact_service_usage",
        "joins": {{
            "dim_product": ("service_id", "product_id"),
            "dim_date": ("date_id", "date_id"),
            "dim_region": ("region_id", "region_id"),
            "dim_customer": ("customer_id", "customer_id")
        }},
        "metrics": {{
            "usage_count": "SUM(f.usage_count)",
            "duration_minutes": "SUM(f.duration_minutes)",
            "cost_incurred": "SUM(f.cost_incurred)"
        }}
    }},

    "fact_finance_snapshot": {{
        "table": "fact_finance_snapshot",
        "joins": {{
            "dim_date": ("date_id", "date_id"),
            "dim_department": ("department_id", "department_id")
        }},
        "metrics": {{
            "total_revenue": "SUM(f.total_revenue)",
            "total_cost": "SUM(f.total_cost)",
            "profit": "SUM(f.profit)",
            "operational_expense": "SUM(f.operational_expense)"
        }}
    }}
}}

DIMENSION_COLUMNS = {{
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
    "full_date": ("dim_date", "full_date")
}}

structured data

Dimension tables describe business entities and change slowly.
Fact tables store measurable business events and grow continuously.

All fact tables reference one or more dimension tables using foreign keys.
Time-based analysis must always use dim_date.)

2. Vector Store (Documents in the vector store follow structured headers.
Each document starts with a Document Type header.
The agent must identify the document type before answering.

Document Types include:
- Company Overview
- Company Policy
- Competitive Intelligence
- Internal Report)

3. Graph Database (Graph Database Description (for Agent):
The graph database stores structured business relationships of SmartX, including products, departments, regions, suppliers, customer segments, issues, and strategic decisions.
It is used to answer questions involving relationships, dependencies, impact analysis, and multi-entity reasoning, such as who is connected to what, why something happened, and which entities influence outcomes.)

GRAPH DATABASE CAPABILITIES:
- Products connected to features, customer segments, suppliers, regions
- Departments connected to issues they handle (e.g., SupplyChain handles Inventory Delay)
- Products affected by issues, departments that respond to issues
- Datasets connected to products and business areas
- Complex relationship queries with multiple hops

For graph queries, identify:
- ENTITIES: specific names like "SmartX Watch", "SupplyChain", "Inventory Delay", "Heart Rate Tracking"
- RELATIONS: relationship types like "HAS_FEATURE", "RESPONDS_TO", "AFFECTED_BY", "TARGETS", "RELATED_TO_DATASET"

Decide which sources to use and WHAT to retrieve.
Do NOT write SQL or Cypher.
Return ONLY valid JSON.
Schema:
{{
  "use_sql": boolean,
  "use_vector": boolean,
  "use_graph": boolean,

   "sql_intent": {{
    "tables": [],
    "filters": {{}},
    "metrics": [],
    "aggregation": null
  }},
  "vector_intent": {{
    "topics": []
  }},

  "graph_intent": {{
    Just the entities and relations
  }}
}}
"""),
    ("human", "{query}")
])

planner_chain = (
    planner_prompt | llm | JsonOutputParser()
)

def plan_retrieval(query: str) -> dict:
    result = planner_chain.invoke({"query": query})
    print(result)
    return result 

#plan=plan_retrieval("What are the key features of SmartX Watch?")
#print(plan)
