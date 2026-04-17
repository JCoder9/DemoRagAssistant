from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.upload_service import UploadService

router = APIRouter(prefix="/api", tags=["upload"])

def get_upload_service():
    return UploadService()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    upload_service = get_upload_service()
    result = await upload_service.process_upload(file)
    return result
