from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import query_routes, upload_routes
from app.settings import settings

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
