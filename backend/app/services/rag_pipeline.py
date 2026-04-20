from typing import List, Dict, Optional
from openai import OpenAI
from app.settings import settings
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


class RAGPipeline:
    def __init__(
        self, 
        embedding_service: EmbeddingService = None,
        vector_store: VectorStore = None,
        chat_model: str = None,
        temperature: float = None,
        top_k: int = None,
        client: OpenAI = None
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or VectorStore()
        self.chat_model = chat_model or settings.CHAT_MODEL
        self.temperature = temperature if temperature is not None else settings.TEMPERATURE
        self.top_k = top_k or settings.TOP_K
        self.client = client
    
    async def query(
        self, 
        question: str, 
        top_k: Optional[int] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        k = top_k or self.top_k
        
        query_embedding = await self.embedding_service.generate_single_embedding(question)
        
        search_results = self.vector_store.search(query_embedding, top_k=k)
        
        if not search_results:
            return {
                "answer": "I don't have enough context to answer this question.",
                "sources": [],
                "context_used": []
            }
        
        if self.client is None:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        context_chunks = [result["text"] for result in search_results]
        context = "\n\n".join(context_chunks)
        
        prompt = self._build_prompt(question, context)
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based only on the provided context. If the answer cannot be found in the context, say 'I cannot answer this based on the provided context.'"
            }
        ]
        
        if chat_history:
            messages.extend(chat_history)
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = self.client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=settings.MAX_TOKENS
        )
        
        answer = response.choices[0].message.content
        
        sources = []
        for result in search_results:
            source = {
                "text": result["text"],
                "score": result["score"]
            }
            if "metadata" in result:
                source["metadata"] = result["metadata"]
            sources.append(source)
        
        return {
            "answer": answer,
            "sources": sources,
            "context_used": context_chunks
        }
    
    def _build_prompt(self, question: str, context: str) -> str:
        return f"""Context:
{context}

Question: {question}

Answer the question based only on the context provided above. If the context doesn't contain enough information to answer the question, say so clearly."""
