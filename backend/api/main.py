from fastapi import FastAPI
from .router import rag_router

app = FastAPI(
    title="Agentic RAG Service",
    version="0.1.0",
    description="FastAPI wrapper around the agentic RAG pipeline.",
)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

# Include the RAG router
app.include_router(rag_router)
