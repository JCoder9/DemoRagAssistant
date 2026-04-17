from typing import List, Dict, Optional
from collections import deque
from app.settings import settings


class ChatMemory:
    def __init__(self, history_limit: int = None):
        self.history_limit = history_limit or settings.CHAT_HISTORY_LIMIT
        self.sessions: Dict[str, deque] = {}
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.history_limit * 2)
        
        self.sessions[session_id].append({
            "role": role,
            "content": content
        })
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        if session_id not in self.sessions:
            return []
        
        return list(self.sessions[session_id])
    
    def clear_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def clear_all(self) -> None:
        self.sessions.clear()
    
    def get_session_count(self) -> int:
        return len(self.sessions)
