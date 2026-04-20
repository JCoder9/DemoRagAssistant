from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from app.services.query_service import QueryService
from app.services.rate_limiter import RateLimiter
from app.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["query"])

rate_limiter = RateLimiter(
    hourly_limit=settings.HOURLY_RATE_LIMIT,
    daily_limit=settings.DAILY_RATE_LIMIT,
    global_monthly_limit=settings.GLOBAL_MONTHLY_LIMIT,
    cooldown_seconds=settings.COOLDOWN_SECONDS
)

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    context_used: list[str]
    demo_notice: Optional[str] = "This is a limited demo. Full version supports higher usage and larger datasets."

def get_query_service():
    return QueryService()

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, http_request: Request):
    try:
        if len(request.question) > settings.MAX_QUERY_LENGTH:
            raise HTTPException(
                status_code=400, 
                detail=f"Query exceeds maximum length of {settings.MAX_QUERY_LENGTH} characters."
            )
        
        client_ip = get_client_ip(http_request)
        
        allowed, message = rate_limiter.check_rate_limit(client_ip)
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_ip}: {message}")
            raise HTTPException(status_code=429, detail=message)
        
        rate_limiter.record_request(client_ip)
        
        query_service = get_query_service()
        result = await query_service.process_query(
            request.question, 
            request.top_k,
            request.session_id
        )
        
        result["demo_notice"] = "This is a limited demo. Full version supports higher usage and larger datasets."
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
