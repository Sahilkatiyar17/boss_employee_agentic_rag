# Boss-Employee Agentic RAG System

<!-- Add your YouTube Live Video link here -->
**🎥 Video Demo:** [[Youtube link]](https://youtu.be/99FtCAakQxo)

---

## 🚀 Project Overview

The **Boss-Employee Agentic RAG System** is a **multi-agent AI framework** designed to simulate a dynamic office workflow where tasks are intelligently assigned and executed by specialized AI agents. This project demonstrates **how agentic RAG pipelines** can be leveraged to create autonomous, problem-solving AI systems.

The system consists of:

1. **Agentic RAG Pipeline** – A retrieval-augmented generation pipeline that can fetch information from multiple sources dynamically:
   - **SQL Database** – For structured data queries  
   - **Vector Store** – For semantic search and fallback retrieval  
   - **Graph Database** – For complex relationship-based queries  

   The pipeline intelligently chooses the best source depending on the query and gracefully falls back to the vector store if the graph database fails.

2. **Multi-Agent Workflow** – A boss-agent assigns tasks to specialized employee agents:
   - **Data Analysis Agent** – A reactive agent that executes data-related tasks dynamically.  
   - **Research Agent** – A planning-oriented agent that first organizes and plans workflow before executing tasks.  

Both agents use the **Agentic RAG pipeline** as a tool for retrieving relevant information.

---

## 🧩 Architecture
<img width="1332" height="352" alt="image" src="https://github.com/user-attachments/assets/d7c1c65f-e638-4be4-8ca3-c3014fb5c6af" />


- **Boss Agent** decides task allocation.  
- **Employee Agents** perform tasks using the **Agentic RAG pipeline**.  
- **Frontend** displays real-time logs of agent operations.  
- Observability is enhanced using **LangSmith**, which helps track errors, latency, and workflow execution.  
  - **Latency:** ~11–15 seconds per query depending on data complexity.

---

## 🧰 Tech Stack

- **Backend**: Python, FastAPI  
- **Frontend**: Streamlit  
- **Databases**:
  - SQLite (SQL database)
  - FAISS/Chroma (Vector Store)
  - Neo4j (Graph Database)  
- **Agentic AI Tools**:
  - **LangChain** – Agentic RAG & workflow orchestration  
  - **LangGraph** – Graph-based reasoning for complex relationships  
  - **LangSmith** – Observability, monitoring, and latency analysis  
- **Environment Management**: `.env` files for secure API keys and configuration  

---

## ⚡ Features

- Fully **autonomous multi-agent task allocation**  
- **Dynamic retrieval** from SQL, vector store, and graph database  
- **Fallback mechanisms** ensure reliability if a data source fails  
- **Observability with LangSmith**: Helps monitor execution flow, errors, and latency  
- **Reactive and planning agents** simulate real-world workflow behaviors  
- **Streamlit frontend** mirrors backend logs in real-time  

---

## 📝 Setup & Installation

### 1. Download Requirements
Download the requirements `.txt` file and install dependencies:

```bash
pip install -r requirements.txt
```
### 2. Backend Setup
Navigate to the backend folder:
``` bash
cd backend
```
### 3.Create a .env file with your API keys and configuration:
```bash

SERPER_API_KEY=
HUGGINGFACEHUB_API_TOKEN=
GOOGLE_API_KEY=

NEO4J_URI=
NEO4J_USERNAME=
NEO4J_PASSWORD=
NEO4J_DATABASE=
AURA_INSTANCEID=
AURA_INSTANCENAME=

# HuggingFace Model (free, no API key needed)
EMBEDDING_MODEL=all-MiniLM-L6-v2
LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=BOSS_EMPLOYEE_AGENTIC_RAG
GROQ_API_KEY_R=
GROQ_API_KEY_DATA=
AGENTIC_API_KEY=
TAVILY_API_KEY=
```
### 4. Run the FastAPI backend:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```
Note: --reload is not required, as the server runs normally.

### 5. Navigate to the frontend folder:
```bash
cd ../frontend
```
### 6. Run the Streamlit app:
``` bash
streamlit run app.py
```

## Repository Structure 

## Future Plans
- Dockerize the project for easy deployment
- Add new employee agents, such as:
- Report Writing Agent
- Other specialized agents for complex workflows
- Enhance graph DB queries and agent reasoning
