from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.query_service import QueryService

router = APIRouter(prefix="/api", tags=["query"])

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

query_service = QueryService()

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        result = await query_service.process_query(request.question, request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
