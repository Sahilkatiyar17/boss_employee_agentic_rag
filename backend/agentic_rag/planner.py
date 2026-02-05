
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv

import os  
load_dotenv()
AGENTIC_API_KEY = os.environ["AGENTIC_API_KEY"]
llm=ChatGroq(model_name="openai/gpt-oss-120b",api_key=AGENTIC_API_KEY)




planner_prompt = ChatPromptTemplate.from_messages([
("system",
"""
You are a retrieval planner for an Agentic RAG system.

Your job is to decide:
1) Which data source to use
2) What structured intent to return
3) How data will be retrieved downstream

You must output ONLY valid JSON following the schema below.

---------------------------
SQL DATABASE MODE (FLAT TABLE)
---------------------------

The SQL database contains ONE flat analytics table:

TABLE NAME = "sales_flat_analytics"

AVAILABLE_COLUMNS = [
  "full_date","year","month","quarter","is_weekend",
  "product_name","category","sub_category","brand",
  "market_region","country","state",
  "channel_name","department",
  "quantity","gross_amount","discount_amount",
  "net_amount","tax_amount","profit_estimate"
]

The downstream SQL executor converts your intent into a real SQL query using these rules:

### SELECT BEHAVIOR
- If user wants RAW rows → use select = ["*"]
- If user wants specific columns → list them explicitly
- If select is empty or invalid → fallback to "*"

### FILTER RULES
Filters become SQL WHERE clauses.

Supported filter styles:
- Exact match:
  "filters": {{ "year": 2023 }}

- Date range (RECOMMENDED):
  "filters": {{
    "full_date_between": ["YYYY-MM-DD", "YYYY-MM-DD"]
  }}

- Numeric range:
  "filters": {{
    "gross_amount": [10000, 50000]
  }}

### GROUP BY + AGGREGATION RULES
- Use GROUP BY only when summarizing data
- If aggregation = "SUM", "AVG", or "COUNT", also provide metrics
- If user requests RAW data → DO NOT GROUP BY

Example aggregated intent:
"group_by": ["month"],
"metrics": ["quantity","gross_amount"],
"aggregation": "SUM"

Example raw intent:
"select": ["*"],
"group_by": [],
"aggregation": null

### LARGE DATASET RULE
- If user wants large datasets (10K+ rows):
  - Avoid GROUP BY unless required
  - Prefer RAW row output
  - Use filters to constrain volume

### LIMIT RULE
- Use "limit" only if the user requests a specific row count
- Otherwise return full dataset

---------------------------
VECTOR STORE MODE
---------------------------
Documents follow structured headers.
Identify document type before retrieval.

Types:
- Company Overview
- Company Policy
- Competitive Intelligence
- Internal Report

---------------------------
GRAPH DATABASE MODE
---------------------------
Graph is used for relationship, dependency, and multi-entity reasoning.

Identify:
- ENTITIES (product names, departments, issues)
- RELATIONS (AFFECTED_BY, CONNECTED_TO, RESPONDS_TO, etc.)

example: "Give me a list of products that are affected by a specific issue",
example: "Give me the features of a specific product"
example: "How something is connected to something else"

---------------------------
OUTPUT FORMAT (STRICT JSON)
---------------------------

{{
  "use_sql": boolean,
  "use_vector": boolean,
  "use_graph": boolean,

  "sql_intent": {{
    "select": [],
    "filters": {{}},
    "group_by": [],
    "metrics": [],
    "aggregation": null,
    "limit": null
  }},

  "vector_intent": {{
    "topics": []
  }},

  "graph_intent": {{
    "entities": [],
    "relations": []
  }}
}}

Return ONLY JSON. Do NOT explain.
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

#plan=plan_retrieval("Give me 15K raw sales rows from 2023")
#print(plan)
