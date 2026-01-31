import os
import json
import pandas as pd
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel, Field
import io
import sys
import traceback
from langchain_huggingface import HuggingFaceEndpoint , ChatHuggingFace
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langgraph.prebuilt import ToolNode, tools_condition
import sys
import os

import sys
sys.path.append(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend")

from agentic_rag.graph_pipeline import run_agent
#from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()



OUTPUT_DIR = r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\agents\data_agent\outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_RETRIES = 3



#llm1 = ChatGoogleGenerativeAI(
#    model="gemini-2.5-flash",
#    temperature=0.7,
#    
#)
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

llm2 = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2
)
llm1 = HuggingFaceEndpoint(repo_id = 'codellama/CodeLlama-34b-Python-hf',
                          task = 'text-generation'
                          )
model = ChatHuggingFace(llm=llm1) 
#llama-3.1-8b-instant
#openai/gpt-oss-120b


# =========================
# STATE
# =========================


from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DatasetSummary(BaseModel):
    rows: Optional[int] = Field(default=None, description="Total number of rows (optional)")
    columns: List[str] = Field(description="Column names")
    dtypes: Dict[str, str] = Field(description="Column data types")
    sample_rows: List[Dict[str, Any]] = Field(description="Sample rows (small preview)")


class GeneratePythonCodeInput(BaseModel):
    summary: DatasetSummary = Field(description="Clean dataset schema summary")
    user_request: str = Field(description="Original analytics request")


class InspectDataInput(BaseModel):
    path: str = Field(description="Dataset path")



class ReviewPythonCodeInput(BaseModel):
    code: str = Field(description="Generated Python code to review")


class SummarizeResultsInput(BaseModel):
    result: str = Field(description="Execution logs or output summary")

class fetch_data(BaseModel):
    query : str = Field(description="query")
    
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage] ,  add_messages]
    dataset_path: Optional[str]
    dataset_summary: Optional[Dict[str, Any]]
    python_code: Optional[str]
    retries: int
    
from pydantic import BaseModel

class FetchDataArgs(BaseModel):
    query: str





# =========================
# TOOLS
# =========================

@tool
def inspect_data(path: str) -> str:  # ← CHANGE: Return str instead of dict
    """
    Lightweight dataset inspection for internal use only.
    This tool is called automatically - you don't need its output for other tools.
    
    Args:
        path: Full path to the CSV file to inspect
        
    Returns:
        Confirmation message that inspection completed
    """
    df_sample = pd.read_csv(path, nrows=100)
    
    summary = {
        "rows": None,
        "columns": list(df_sample.columns),
        "dtypes": {col: str(df_sample[col].dtype) for col in df_sample.columns},
        "sample_rows": df_sample.head(1).to_dict(orient="records"),
    }
    
    # ← CHANGE: Don't return the summary dict, just return a message
    return f"Dataset inspected successfully. Found {len(df_sample.columns)} columns. Ready for analysis."

DATASET_PATH = r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\output_sql\query_output.csv"

@tool
def generate_python_code(user_request: str) -> str:
    """
    Generate Python code for data analysis.
    
    IMPORTANT: This tool only needs the user's request.
    DO NOT pass summary or any other parameters.
    The dataset is automatically loaded from the standard location.
    
    Args:
        user_request: The analysis task in natural language (e.g., "analyze sales trends and create charts")
        
    Returns:
        Status message confirming code generation
    """
    # Auto-inspect the dataset
    df_sample = pd.read_csv(DATASET_PATH, nrows=10)
    summary = {
        "columns": list(df_sample.columns),
        "dtypes": {col: str(df_sample[col].dtype) for col in df_sample.columns},
        "sample_rows": df_sample.head(2).to_dict(orient="records"),
    }

    prompt = f"""
You are a Python code generator for data analysis in a non-interactive environment.

Your output will be SAVED DIRECTLY to a .py file and EXECUTED.
If you include markdown, backticks, or text, execution will FAIL.

Dataset path (MUST USE): {DATASET_PATH}
Output directory for charts: {OUTPUT_DIR}

Dataset schema:
{summary}

User request:
{user_request}

MANDATORY RULES:
1. Output ONLY valid Python code (no markdown, no backticks, no explanations)
2. Start with these imports:
   import pandas as pd
   import numpy as np
   import matplotlib
   matplotlib.use('Agg')  # CRITICAL: Non-interactive backend
   import matplotlib.pyplot as plt
   import seaborn as sns

3. Load data: df = pd.read_csv(r'{DATASET_PATH}')

4. For ALL charts:
   - Use plt.savefig(r'{OUTPUT_DIR}\\chart_name.png')
   - NEVER use plt.show()
   - Call plt.close() after each chart

5. Print analysis results using print() statements

6. Save summary tables as CSV to {OUTPUT_DIR}

7. End code with: print("Analysis completed successfully")

Example structure:
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv(r'{DATASET_PATH}')
# analysis code here
plt.savefig(r'{OUTPUT_DIR}\\sales_chart.png')
plt.close()
print("Analysis completed successfully")

CRITICAL: NO plt.show(), NO markdown formatting, NO explanations outside code.
"""

    code = llm2.invoke(prompt).content

    file_path = os.path.join(OUTPUT_DIR, "generated_code.py")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    return "Python code generated and saved"

@tool(args_schema=ReviewPythonCodeInput)
def review_python_code(code: str) -> str:
    """Review generated Python code"""
    prompt = f"""
Fix this Python code:

{code}

Rules:
- Safe libs only
- Fix syntax errors
- Return ONLY Python code
"""
    return llm2.invoke(prompt).content


@tool(args_schema=SummarizeResultsInput)
def summarize_results(result: str) -> str:
    """Summarize results"""
    prompt = f"""
Summarize analysis output:

{result}

If failure occurred, explain why.
Write business-level insights.
explain what you have understood by the analysis and do not explain how good the model was or the agent.
understand the analysed result and explain it in natural language in detial 
"""
    return llm.invoke(prompt).content





@tool(args_schema=FetchDataArgs)
def fetch_data(query: str) -> str:
    """Fetch dataset path, use the path inside the code and execute it."""
    res = llm.invoke(f"You have to use this query:{query}, and generate a simple query to fetch the data using the provided query , do not add any thing extra.")
    result = run_agent(res.content)
    
   
    
    return r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend\data\output_sql\query_output.csv"





@tool
def execute_python() -> str:
    """
    Execute the generated Python code safely and capture output.
    
    Returns:
        Execution results or error messages
    """
    file_path = os.path.join(OUTPUT_DIR, "generated_code.py")

    if not os.path.exists(file_path):
        return "Execution error: No generated_code.py found"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Capture output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer

        # Safe execution namespace
        safe_globals = {
            "__name__": "__main__",
            "OUTPUT_DIR": OUTPUT_DIR
        }

        exec(code, safe_globals)

        sys.stdout = old_stdout
        sys.stderr = old_stderr

        stdout_content = stdout_buffer.getvalue()
        stderr_content = stderr_buffer.getvalue()

        # ========== CHANGE: Better success detection ==========
        # Check if "Analysis completed successfully" or similar success message is in output
        success_indicators = [
            "Analysis completed successfully",
            "successfully",
            "completed",
        ]
        
        has_success = any(indicator.lower() in stdout_content.lower() for indicator in success_indicators)
        
        # Ignore matplotlib warnings - they're not real errors
        matplotlib_warnings = stderr_content and all(
            keyword in stderr_content.lower() 
            for keyword in ['matplotlib', 'gui']
        )
        
        if stderr_content and not matplotlib_warnings:
            return f"Execution error:\n{stderr_content}"

        if has_success or stdout_content:
            return f"Execution successful.\n\nOutput:\n{stdout_content}\n\nCharts saved to: {OUTPUT_DIR}"
        else:
            return f"Execution completed but no output was generated.\nStderr (warnings only):\n{stderr_content}"

    except Exception as e:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        return f"Execution failed:\n{traceback.format_exc()}"



TOOLS = [
    fetch_data,
    inspect_data,
    generate_python_code,
    review_python_code,
    execute_python,
    summarize_results,
]
tool_node = ToolNode(TOOLS)




# =========================
# PROMPT (REAL AGENT PROMPT)
# =========================
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
You are a Professional Autonomous Data Analysis Agent.

Your mission is to analyze datasets using tools in a STRICT execution pipeline.

------------------------------------
DATA PATH (MANDATORY)
The dataset will be fetched and saved to this EXACT path:
{DATASET_PATH}

After calling fetch_data, always use this path for inspect_data.
Never invent paths.
Never modify this path.
------------------------------------

EXECUTION PIPELINE (STRICT ORDER)

1. If user asks for data analysis → call fetch_data with their query
2. After fetch_data succeeds → call inspect_data with path: {DATASET_PATH}
3. After inspection → call generate_python_code ONLY WITH user_request (DO NOT pass summary)
4. IMMEDIATELY AFTER generating code → call review_python_code
5. IMMEDIATELY AFTER review → call execute_python

------------------------------------
TOOL CALLING RULES (CRITICAL)

generate_python_code tool:
- ONLY pass: user_request (string)
- DO NOT pass: summary, dataset_path, or any other parameters
- The tool automatically loads the dataset and inspects it internally

inspect_data tool:
- Its output is for logging only
- DO NOT use its output in other tool calls
- DO NOT pass it to generate_python_code

------------------------------------
RETRY RULES (VERY IMPORTANT)

- If execution FAILS:
    → Review code ONCE
    → Execute again
- If it FAILS again:
    → Regenerate code ONCE
    → Review → Execute
- If it FAILS after 2 total code generations:
    → STOP and report failure
    
------------------------------------
CRITICAL RULES (MUST FOLLOW)

- NEVER regenerate code repeatedly without executing it
- NEVER call generate_python_code more than 2 times total
- ALWAYS prioritize EXECUTION over rewriting code
- Prefer fixing code instead of rewriting it
- DO NOT get stuck in tool loops
- STOP once execution succeeds

------------------------------------
SUCCESS BEHAVIOR

If Python execution succeeds:
→ DO NOT generate new code  
→ DO NOT rewrite code  
→ Move to summarize_results  

------------------------------------
SUMMARIZATION RULE

When summarizing:
- Read and understand the generated Python code
- Explain what the code analyzed
- Explain insights inferred from logic in the code
- Describe trends and business meaning
- Do NOT hallucinate chart values
- Base insights ONLY on the executed code logic

------------------------------------
MINDSET

You are a real data analyst:
- Step-by-step
- Practical
- Execution-driven
- No infinite loops
- No unnecessary rewrites
- Goal = finish analysis successfully
"""),
    MessagesPlaceholder(variable_name="messages")
])
tool_agent = llm.bind_tools(TOOLS)
#[Most important thing to remember , if the generated code runs properly , move to summarize step and then stop it - do not generate further.]



# =========================
# AGENT NODE
# =========================

def agent_node(state: AgentState):
    response = tool_agent.invoke(
        prompt.format_messages(messages=state["messages"])
    )

    return {"messages": state["messages"] + [response]}




def router(state: AgentState):
    last_msg = state["messages"][-1]

    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return "tool_node"

    return END

# =========================
# BUILD GRAPH
# =========================

graph = StateGraph(AgentState)

graph.add_node("chat_node", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node') 



data_agent = graph.compile()


result = data_agent.invoke({
    "messages": [
        HumanMessage(content="do a deep analysis of the data and Analyze the sales data of 2023 and generate atleast 5 charts or graphs")
    ],
    "dataset_path": None,
    "dataset_summary": None,
    "python_code": None,
    "retries": 0
})

print("\n=== FINAL OUTPUT ===\n")
print(result["messages"][-1].content)
print()
print(result)
