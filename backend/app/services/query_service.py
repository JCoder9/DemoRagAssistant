from app.services.rag_pipeline import RAGPipeline

class QueryService:
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
    
    async def process_query(self, question: str, top_k: int):
        result = await self.rag_pipeline.query(question, top_k)
        return result
