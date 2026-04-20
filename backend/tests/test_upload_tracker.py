import pytest
from app.services.upload_tracker import UploadTracker


class TestUploadTracker:
    
    def test_first_upload_allowed(self):
        tracker = UploadTracker(max_uploads_per_session=5, max_file_size_mb=5)
        can_upload, message = tracker.can_upload("session1", 1024 * 1024)
        assert can_upload is True
        assert message == ""
    
    def test_file_size_limit(self):
        tracker = UploadTracker(max_uploads_per_session=5, max_file_size_mb=2)
        file_size = 3 * 1024 * 1024
        
        can_upload, message = tracker.can_upload("session1", file_size)
        assert can_upload is False
        assert "exceeds maximum limit" in message
    
    def test_upload_count_limit(self):
        tracker = UploadTracker(max_uploads_per_session=3, max_file_size_mb=5)
        session_id = "session1"
        file_size = 1024 * 1024
        
        for i in range(3):
            can_upload, _ = tracker.can_upload(session_id, file_size)
            assert can_upload is True
            tracker.record_upload(session_id)
        
        can_upload, message = tracker.can_upload(session_id, file_size)
        assert can_upload is False
        assert "Upload limit reached" in message
    
    def test_different_sessions_independent(self):
        tracker = UploadTracker(max_uploads_per_session=2, max_file_size_mb=5)
        file_size = 1024 * 1024
        
        tracker.record_upload("session1")
        tracker.record_upload("session1")
        
        can_upload, _ = tracker.can_upload("session2", file_size)
        assert can_upload is True
    
    def test_get_upload_count(self):
        tracker = UploadTracker()
        session_id = "session1"
        
        assert tracker.get_upload_count(session_id) == 0
        
        tracker.record_upload(session_id)
        assert tracker.get_upload_count(session_id) == 1
        
        tracker.record_upload(session_id)
        assert tracker.get_upload_count(session_id) == 2
    
    def test_reset_session(self):
        tracker = UploadTracker()
        session_id = "session1"
        
        tracker.record_upload(session_id)
        tracker.record_upload(session_id)
        assert tracker.get_upload_count(session_id) == 2
        
        tracker.reset_session(session_id)
        assert tracker.get_upload_count(session_id) == 0
    
    def test_file_size_at_exact_limit(self):
        tracker = UploadTracker(max_file_size_mb=5)
        file_size = 5 * 1024 * 1024
        
        can_upload, message = tracker.can_upload("session1", file_size)
        assert can_upload is True
