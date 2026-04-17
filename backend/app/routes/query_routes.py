from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.query_service import QueryService

router = APIRouter(prefix="/api", tags=["query"])

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    context_used: list[str]

def get_query_service():
    return QueryService()

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        query_service = get_query_service()
        result = await query_service.process_query(
            request.question, 
            request.top_k,
            request.session_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
