import os

from backend.agentic_rag.graph_pipeline import run_agent
# Load environment variables from .env (same as original pipeline)


# Import the compiled LangGraph agent from the existing pipeline package
# Using absolute import because this file lives under `backend/api`
from backend.agentic_rag.graph_pipeline import agent

def _run(query: str):
    """Execute the agentic RAG pipeline for a single query.
    Returns a tuple ``(answer: str, context: dict)``.
    """
    result = agent.invoke({"query": query})
    # The original pipeline returns a dict with keys 'answer' and 'context'
    return result.get("answer"), result.get("context")



def get_pipeline():
    return run_agent
