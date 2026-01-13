
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
1. SQL Database (sales, products, customers, marketing, inventory)
2. Vector Store (business reports, strategy docs, operational notes)
3. Graph Database (product, region, department, dataset relationships)

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
    "entities": [],
    "relations": []
  }}
}}
"""),
    ("human", "{query}")
])

planner_chain = (
    planner_prompt | llm | JsonOutputParser()
)

def plan_retrieval(query: str) -> dict:
    return planner_chain.invoke({"query": query})

plan=plan_retrieval("What are the key features of SmartX Watch?")
print(plan)
