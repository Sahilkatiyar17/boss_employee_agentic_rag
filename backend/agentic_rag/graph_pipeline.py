from langgraph.graph import StateGraph
from typing import TypedDict
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


from backend.agentic_rag.planner import plan_retrieval

from backend.agentic_rag.sql_tool import run_sql
from backend.agentic_rag.vector_tool import run_vector
from backend.agentic_rag.graph_tool import get_graph_context
from backend.agentic_rag.answer import generate_answer

class AgentState(TypedDict):
    query: str
    plan: dict
    context: str
    answer: str


def planner_node(state):
    result = plan_retrieval(state["query"])
    print(result)
    return {"plan": result }


def retrieval_node(state):
    plan = state["plan"]
    context_parts = []

    if plan["use_sql"]:
        context_parts.append("[SQL]\n" + run_sql(plan["sql_intent"]))

    if plan["use_vector"]:
        context_parts.append("[VECTOR]\n" + run_vector(plan["vector_intent"]))

    if plan["use_graph"]:
        context_parts.append("[GRAPH]\n" + get_graph_context(plan["graph_intent"]))

    return {"context": "\n\n".join(context_parts)}


def answer_node(state):
    return {
        "answer": generate_answer(state["query"], state["context"])
    }


graph = StateGraph(AgentState)
graph.add_node("planner", planner_node)
graph.add_node("retriever", retrieval_node)
graph.add_node("answer", answer_node)

graph.set_entry_point("planner")
graph.add_edge("planner", "retriever")
graph.add_edge("retriever", "answer")

agent = graph.compile()

def run_agent(query: str):
    """Single public entry point for FastAPI"""
    return agent.invoke({"query": query})


#print(run_agent("What are the vision,mission, goals of the Smart tech ?"))

#if __name__ == "__main__":
    #result = agent.invoke({
    #    "query": "give me the data of sales of 2023 ",
    #})
#print(result["answer"])