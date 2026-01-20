from pydantic import BaseModel
from typing import Any, Dict, Optional

class QueryRequest(BaseModel):
    query: str

class AnswerResponse(BaseModel):
    answer: str
    # Optional field to return raw sources if needed later
    sources: Optional[Dict[str, Any]] = None
