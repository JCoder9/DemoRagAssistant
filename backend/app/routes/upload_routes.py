from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.services.upload_service import UploadService
from app.services.upload_tracker import UploadTracker
from app.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

upload_tracker = UploadTracker(
    max_uploads_per_session=settings.MAX_UPLOADS_PER_SESSION,
    max_file_size_mb=settings.MAX_FILE_SIZE_MB
)

def get_upload_service():
    return UploadService()

def get_session_id(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), request: Request = None):
    try:
        session_id = get_session_id(request)
        
        content = await file.read()
        file_size = len(content)
        
        can_upload, error_msg = upload_tracker.can_upload(session_id, file_size)
        if not can_upload:
            logger.warning(f"Upload rejected for {session_id}: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        await file.seek(0)
        
        upload_service = get_upload_service()
        result = await upload_service.process_upload(file)
        
        upload_tracker.record_upload(session_id)
        
        remaining = settings.MAX_UPLOADS_PER_SESSION - upload_tracker.get_upload_count(session_id)
        result["uploads_remaining"] = remaining
        result["demo_notice"] = f"Demo limit: {remaining} uploads remaining in this session."
        
        logger.info(f"Upload successful for {session_id}: {file.filename}")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
