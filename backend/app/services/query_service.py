from typing import Optional
from app.services.rag_pipeline import RAGPipeline
from app.services.chat_memory import ChatMemory

class QueryService:
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.chat_memory = ChatMemory()
    
    async def process_query(self, question: str, top_k: int, session_id: Optional[str] = None):
        chat_history = None
        if session_id:
            chat_history = self.chat_memory.get_history(session_id)
        
        result = await self.rag_pipeline.query(question, top_k, chat_history)
        
        if session_id:
            self.chat_memory.add_message(session_id, "user", question)
            self.chat_memory.add_message(session_id, "assistant", result["answer"])
        
        return result
