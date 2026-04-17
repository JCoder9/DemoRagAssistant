import pytest
from app.services.chat_memory import ChatMemory


class TestChatMemory:
    
    def test_add_and_get_message(self):
        memory = ChatMemory(history_limit=3)
        
        memory.add_message("session1", "user", "Hello")
        memory.add_message("session1", "assistant", "Hi there!")
        
        history = memory.get_history("session1")
        
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"
    
    def test_history_limit(self):
        memory = ChatMemory(history_limit=2)
        
        memory.add_message("session1", "user", "Message 1")
        memory.add_message("session1", "assistant", "Response 1")
        memory.add_message("session1", "user", "Message 2")
        memory.add_message("session1", "assistant", "Response 2")
        memory.add_message("session1", "user", "Message 3")
        memory.add_message("session1", "assistant", "Response 3")
        
        history = memory.get_history("session1")
        
        assert len(history) == 4
        assert history[0]["content"] == "Message 2"
        assert history[-1]["content"] == "Response 3"
    
    def test_multiple_sessions(self):
        memory = ChatMemory()
        
        memory.add_message("session1", "user", "Hello from session 1")
        memory.add_message("session2", "user", "Hello from session 2")
        
        history1 = memory.get_history("session1")
        history2 = memory.get_history("session2")
        
        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["content"] == "Hello from session 1"
        assert history2[0]["content"] == "Hello from session 2"
    
    def test_get_nonexistent_session(self):
        memory = ChatMemory()
        
        history = memory.get_history("nonexistent")
        
        assert history == []
    
    def test_clear_session(self):
        memory = ChatMemory()
        
        memory.add_message("session1", "user", "Hello")
        memory.add_message("session1", "assistant", "Hi")
        
        assert len(memory.get_history("session1")) == 2
        
        memory.clear_session("session1")
        
        assert memory.get_history("session1") == []
    
    def test_clear_all(self):
        memory = ChatMemory()
        
        memory.add_message("session1", "user", "Hello 1")
        memory.add_message("session2", "user", "Hello 2")
        
        assert memory.get_session_count() == 2
        
        memory.clear_all()
        
        assert memory.get_session_count() == 0
        assert memory.get_history("session1") == []
        assert memory.get_history("session2") == []
    
    def test_session_count(self):
        memory = ChatMemory()
        
        assert memory.get_session_count() == 0
        
        memory.add_message("session1", "user", "Hello")
        assert memory.get_session_count() == 1
        
        memory.add_message("session2", "user", "Hello")
        assert memory.get_session_count() == 2
        
        memory.add_message("session1", "user", "Another message")
        assert memory.get_session_count() == 2
