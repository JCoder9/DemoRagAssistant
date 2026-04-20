from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import query_routes, upload_routes
from app.settings import settings
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_routes.router)
app.include_router(upload_routes.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("RAG Assistant API starting up")
    logger.info(f"Rate limits: {settings.HOURLY_RATE_LIMIT}/hour, {settings.DAILY_RATE_LIMIT}/day")
    logger.info(f"Global monthly limit: {settings.GLOBAL_MONTHLY_LIMIT}")
    logger.info(f"Upload limits: {settings.MAX_UPLOADS_PER_SESSION} files, {settings.MAX_FILE_SIZE_MB}MB max")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("RAG Assistant API shutting down")
