import sys
sys.path.append(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend")

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
import os
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from langchain.tools import tool
from langchain_core.prompts import PromptTemplate , ChatPromptTemplate
from langchain_core.messages import SystemMessage
from agents.data_agent.agent_1 import data_agent
from agents.research_agent.agent import research_agent
load_dotenv()
agentic_api_key = os.environ["AGENTIC_API_KEY"]


def research_run(topic: str):
    out = research_agent.invoke(
        {
            "topic": topic,
            "mode": "",
            "needs_research": False,
            "queries": [],
            "evidence": [],
            "plan": None,
            "sections": [],
            "final": "",
        }
    )

    return out

def data_run(topic: str):
    result = data_agent.invoke({
        "messages": [
            HumanMessage(content=topic)
        ],
        "dataset_path": None,
        "dataset_summary": None,
        "python_code": None,
        "retries": 0
    })

    return result 


@tool
def research_agent_tool(topic: str) -> str:
    """
     STRICT USE ONLY FOR:

    - research
    - company comparison
    - competitor analysis
    - industry insights
    - concept explanation
    - general knowledge research

    DO NOT USE FOR:
    - data analysis
    - datasets
    - calculations
    - statistics
    """
    result = research_run(topic)
    return str(result['final'])


@tool
def data_agent_tool(topic: str) -> str:
    """
    STRICT USE ONLY FOR:

    - dataset analysis
    - statistical calculations
    - charts
    - numerical processing
    - python analysis

    DO NOT USE FOR:
    - research
    - company comparison
    - conceptual explanations
    - market analysis
    """
    result = data_run(topic)
    return str(result["messages"][-1].content)



class BossState(TypedDict):
    messages: List[BaseMessage]
    




system_prompt = """
You are a STRICT BOSS AGENT that delegates work to employees.

You MUST follow the TOOL DECISION PROTOCOL below BEFORE using ANY tool.
Your task is to just decide which tool to use , do not think any thing else and the take the decisions.
your job - to decide which tool to use.(everytime you have to choose a tool.)
--------------------------------
TOOL DECISION PROTOCOL
--------------------------------

STEP 1 — CLASSIFY USER INTENT:

A. DATA ANALYSIS TASK
   Only if user explicitly says:
   - analyze data
   - dataset analysis
   - statistics
   - calculations
   - charts
   - numerical analysis
   - run python
   - perform data analysis

B. RESEARCH TASK
   Only if user explicitly says:
   - research
   - compare companies
   - market research
   - competitor analysis
   - industry analysis
   - explain concept
   - literature review
   - gather information

C. HYBRID TASK
   Only if user clearly requests BOTH:
   - data analysis FIRST
   - THEN research using results

D. DIRECT RESPONSE
   If neither research nor data analysis required.

--------------------------------
TOOL USAGE RULES
--------------------------------

RULE 1:
If intent = RESEARCH → use ONLY research_agent_tool

RULE 2:
If intent = DATA ANALYSIS → use ONLY data_agent_tool

RULE 3:
If intent = HYBRID →
   Step 1: data_agent_tool
   Step 2: research_agent_tool

RULE 4:
NEVER call BOTH tools unless HYBRID task explicitly stated.

RULE 5:
NEVER call tools just to "improve" answers.

RULE 6:
DO NOT guess or experiment with tools.

RULE 7:
If unsure → ASK USER FOR CLARIFICATION.

--------------------------------
CRITICAL BEHAVIOR
--------------------------------

You are a STRICT MANAGER.
You DO NOT over-delegate.
You DO NOT try unnecessary tools.

Always produce final answer after tool usage.
"""

# ==============================
# PROMPT TEMPLATE
# ==============================

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)




llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=agentic_api_key,
    temperature=0
)

tools = [research_agent_tool, data_agent_tool]

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

boss_agent = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

def boss_run(query: str):
    return boss_agent.invoke(
        {
            "input": query
        }
    )

#a = boss_run("Do research , where compare the features of our headset with our competitor's(boat company) headset features ")
#print(a['output'])
