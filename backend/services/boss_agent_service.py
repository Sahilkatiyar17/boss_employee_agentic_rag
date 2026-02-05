import sys

# ADD BACKEND ROOT
sys.path.append(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend")

# IMPORT YOUR EXISTING BOSS AGENT
from agents.master_agent.main import boss_run


# =========================
# SERVICE WRAPPER
# =========================

def run_boss(query: str):

    result = boss_run(query)

    # Your boss_run returns dict → { "output": ... }
    if isinstance(result, dict) and "output" in result:
        return result["output"]

    return str(result)
