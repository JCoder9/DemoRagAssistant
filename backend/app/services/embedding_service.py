from typing import List, Dict
from openai import OpenAI
from app.settings import settings


class EmbeddingService:
    def __init__(self, model: str = None):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model or settings.EMBEDDING_MODEL
        self.embedding_dim = 1536 if "3-small" in self.model else 3072
    
    async def generate_embeddings(
        self, 
        texts: List[str], 
        metadata: List[Dict] = None
    ) -> List[Dict]:
        if not texts:
            return []
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size] if metadata else [{}] * len(batch)
            
            response = self.client.embeddings.create(
                input=batch,
                model=self.model
            )
            
            for j, embedding_data in enumerate(response.data):
                result = {
                    "embedding": embedding_data.embedding,
                    "text": batch[j],
                    "index": i + j,
                }
                
                if batch_metadata[j]:
                    result["metadata"] = batch_metadata[j]
                
                all_embeddings.append(result)
        
        return all_embeddings
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        
        response = self.client.embeddings.create(
            input=[text],
            model=self.model
        )
        
        return response.data[0].embedding
