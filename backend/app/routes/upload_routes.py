from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.upload_service import UploadService

router = APIRouter(prefix="/api", tags=["upload"])

upload_service = UploadService()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    result = await upload_service.process_upload(file)
    return result
