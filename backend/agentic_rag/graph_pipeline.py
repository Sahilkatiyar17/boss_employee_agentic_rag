from langgraph.graph import StateGraph
from typing import TypedDict

from planner import plan_retrieval
from sql_tool import run_sql
from vector_tool import run_vector
from graph_tool import run_graph
from answer import generate_answer

class AgentState(TypedDict):
    query: str
    plan: dict
    context: str
    answer: str


def planner_node(state):
    return {"plan": plan_retrieval(state["query"])}


def retrieval_node(state):
    plan = state["plan"]
    context_parts = []

    if plan["use_sql"]:
        context_parts.append("[SQL]\n" + run_sql(plan["sql_intent"]))

    if plan["use_vector"]:
        context_parts.append("[VECTOR]\n" + run_vector(plan["vector_intent"]))

    if plan["use_graph"]:
        context_parts.append("[GRAPH]\n" + run_graph(plan["graph_intent"]))

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


result = agent.invoke({
    "query": "Why did headset sales drop in South India?"
})

print(result["answer"])
