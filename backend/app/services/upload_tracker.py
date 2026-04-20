from typing import Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class UploadTracker:
    def __init__(
        self,
        max_uploads_per_session: int = 5,
        max_file_size_mb: int = 5,
        session_timeout_hours: int = 24
    ):
        self.max_uploads_per_session = max_uploads_per_session
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.session_timeout = timedelta(hours=session_timeout_hours)
        
        self.upload_counts: Dict[str, tuple] = {}
    
    def can_upload(self, session_id: str, file_size: int) -> tuple[bool, str]:
        if file_size > self.max_file_size_bytes:
            max_mb = self.max_file_size_bytes / (1024 * 1024)
            return False, f"File size exceeds maximum limit of {max_mb:.0f}MB."
        
        now = datetime.now()
        
        if session_id in self.upload_counts:
            last_upload, count = self.upload_counts[session_id]
            
            if now - last_upload > self.session_timeout:
                self.upload_counts[session_id] = (now, 0)
                count = 0
            
            if count >= self.max_uploads_per_session:
                return False, f"Upload limit reached. Maximum {self.max_uploads_per_session} documents per session."
        
        return True, ""
    
    def record_upload(self, session_id: str) -> None:
        now = datetime.now()
        
        if session_id in self.upload_counts:
            last_upload, count = self.upload_counts[session_id]
            if now - last_upload > self.session_timeout:
                self.upload_counts[session_id] = (now, 1)
            else:
                self.upload_counts[session_id] = (now, count + 1)
        else:
            self.upload_counts[session_id] = (now, 1)
        
        count = self.upload_counts[session_id][1]
        logger.info(f"Upload recorded for session {session_id}: {count}/{self.max_uploads_per_session}")
    
    def get_upload_count(self, session_id: str) -> int:
        if session_id not in self.upload_counts:
            return 0
        
        last_upload, count = self.upload_counts[session_id]
        if datetime.now() - last_upload > self.session_timeout:
            return 0
        
        return count
    
    def reset_session(self, session_id: str) -> None:
        if session_id in self.upload_counts:
            del self.upload_counts[session_id]
            logger.info(f"Reset upload count for session {session_id}")
