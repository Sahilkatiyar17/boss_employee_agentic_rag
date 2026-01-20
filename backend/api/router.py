from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

from .schemas import QueryRequest, AnswerResponse
from .dependencies import get_pipeline

rag_router = APIRouter(prefix="/rag", tags=["RAG"])

@rag_router.post("/answer", response_model=AnswerResponse)
def get_answer(request: QueryRequest, pipeline=Depends(get_pipeline)):
    try:
        result = pipeline(request.query)
        return AnswerResponse(answer=result["answer"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
