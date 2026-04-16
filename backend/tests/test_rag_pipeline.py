import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.services.rag_pipeline import RAGPipeline
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


@pytest.fixture(autouse=True)
def mock_openai_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")


class TestRAGPipeline:
    
    @pytest.fixture
    def mock_embedding_service(self):
        service = Mock(spec=EmbeddingService)
        service.generate_single_embedding = AsyncMock(return_value=[0.1] * 1536)
        return service
    
    @pytest.fixture
    def mock_vector_store(self):
        store = Mock(spec=VectorStore)
        return store
    
    @pytest.fixture
    def mock_openai_client(self):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test answer based on the context."
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client
    
    @pytest.mark.asyncio
    async def test_query_with_results(self, mock_embedding_service, mock_vector_store, mock_openai_client):
        mock_vector_store.search.return_value = [
            {
                "text": "Python is a programming language",
                "score": 0.1,
                "metadata": {"source": "doc1"}
            },
            {
                "text": "Python is widely used for data science",
                "score": 0.2,
                "metadata": {"source": "doc2"}
            }
        ]
        
        pipeline = RAGPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            client=mock_openai_client
        )
        
        result = await pipeline.query("What is Python?", top_k=2)
        
        assert "answer" in result
        assert "sources" in result
        assert "context_used" in result
        assert len(result["sources"]) == 2
        assert len(result["context_used"]) == 2
        assert result["sources"][0]["text"] == "Python is a programming language"
        assert result["sources"][0]["metadata"]["source"] == "doc1"
        
        mock_embedding_service.generate_single_embedding.assert_called_once_with("What is Python?")
        mock_vector_store.search.assert_called_once()
        mock_openai_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_no_results(self, mock_embedding_service, mock_vector_store):
        mock_vector_store.search.return_value = []
        
        pipeline = RAGPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store
        )
        
        result = await pipeline.query("What is quantum computing?")
        
        assert result["answer"] == "I don't have enough context to answer this question."
        assert result["sources"] == []
        assert result["context_used"] == []
        
        mock_embedding_service.generate_single_embedding.assert_called_once()
        mock_vector_store.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query_system_prompt(self, mock_embedding_service, mock_vector_store, mock_openai_client):
        mock_vector_store.search.return_value = [
            {"text": "Test context", "score": 0.1}
        ]
        
        pipeline = RAGPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            client=mock_openai_client
        )
        
        await pipeline.query("Test question?")
        
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "based only on the provided context" in messages[0]["content"]
        assert messages[1]["role"] == "user"
        assert "Test question?" in messages[1]["content"]
        assert "Test context" in messages[1]["content"]
    
    @pytest.mark.asyncio
    async def test_query_uses_correct_model_and_temperature(self, mock_embedding_service, mock_vector_store, mock_openai_client):
        mock_vector_store.search.return_value = [
            {"text": "Context", "score": 0.1}
        ]
        
        pipeline = RAGPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            chat_model="gpt-4o",
            temperature=0.5,
            client=mock_openai_client
        )
        
        await pipeline.query("Question?")
        
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-4o"
        assert call_args.kwargs["temperature"] == 0.5
    
    @pytest.mark.asyncio
    async def test_build_prompt_format(self, mock_embedding_service, mock_vector_store):
        pipeline = RAGPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store
        )
        
        prompt = pipeline._build_prompt(
            "What is AI?",
            "Artificial Intelligence is the simulation of human intelligence."
        )
        
        assert "Context:" in prompt
        assert "Question: What is AI?" in prompt
        assert "Artificial Intelligence is the simulation of human intelligence." in prompt
        assert "based only on the context" in prompt
    
    @pytest.mark.asyncio
    async def test_query_without_metadata(self, mock_embedding_service, mock_vector_store, mock_openai_client):
        mock_vector_store.search.return_value = [
            {"text": "Test without metadata", "score": 0.1}
        ]
        
        pipeline = RAGPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            client=mock_openai_client
        )
        
        result = await pipeline.query("Question?")
        
        assert len(result["sources"]) == 1
        assert result["sources"][0]["text"] == "Test without metadata"
        assert result["sources"][0]["score"] == 0.1
        assert "metadata" not in result["sources"][0]
