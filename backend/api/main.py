from fastapi import FastAPI
from pydantic import BaseModel
import sys
sys.path.append(r"F:\sahil\2025-2026\Project_DS\boss_employee_agentic_rag\backend")
from services.boss_agent_service import run_boss
from dotenv import load_dotenv
import os

# LOAD ENVIRONMENT VARIABLES ON SERVER START
load_dotenv()
app = FastAPI(
    title="Boss Agent API",
    version="1.0"
)

# ======================
# REQUEST MODEL
# ======================

class ChatRequest(BaseModel):
    query: str


# ======================
# HEALTH CHECK
# ======================

@app.get("/")
def health():
    return {"status": "Boss Agent API Running"}


# ======================
# MAIN CHAT ENDPOINT
# ======================

@app.post("/chat")
def chat(req: ChatRequest):

    response = run_boss(req.query)

    return {
        "response": response
    }
