import pytest
from unittest.mock import Mock, patch
from app.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    
    @pytest.mark.asyncio
    @patch('app.services.embedding_service.settings')
    @patch('app.services.embedding_service.OpenAI')
    async def test_generate_single_embedding(self, mock_openai_class, mock_settings):
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.EMBEDDING_MODEL = "text-embedding-3-small"
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        service = EmbeddingService()
        embedding = await service.generate_single_embedding("test text")
        
        assert len(embedding) == 1536
        assert embedding[0] == 0.1
        mock_client.embeddings.create.assert_called_once_with(
            input=["test text"],
            model="text-embedding-3-small"
        )
    
    @pytest.mark.asyncio
    @patch('app.services.embedding_service.settings')
    @patch('app.services.embedding_service.OpenAI')
    async def test_generate_embeddings_batch(self, mock_openai_class, mock_settings):
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.EMBEDDING_MODEL = "text-embedding-3-small"
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1] * 1536),
            Mock(embedding=[0.2] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        service = EmbeddingService()
        texts = ["text one", "text two"]
        metadata = [{"source": "doc1"}, {"source": "doc2"}]
        
        results = await service.generate_embeddings(texts, metadata)
        
        assert len(results) == 2
        assert results[0]["text"] == "text one"
        assert results[0]["metadata"]["source"] == "doc1"
        assert len(results[0]["embedding"]) == 1536
        assert results[1]["text"] == "text two"
        assert results[1]["metadata"]["source"] == "doc2"
    
    @pytest.mark.asyncio
    @patch('app.services.embedding_service.settings')
    @patch('app.services.embedding_service.OpenAI')
    async def test_generate_embeddings_empty_list(self, mock_openai_class, mock_settings):
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.EMBEDDING_MODEL = "text-embedding-3-small"
        
        service = EmbeddingService()
        results = await service.generate_embeddings([])
        
        assert results == []
    
    @pytest.mark.asyncio
    @patch('app.services.embedding_service.settings')
    @patch('app.services.embedding_service.OpenAI')
    async def test_missing_api_key_raises_error(self, mock_openai_class, mock_settings):
        mock_settings.OPENAI_API_KEY = None
        mock_settings.EMBEDDING_MODEL = "text-embedding-3-small"
        
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        service = EmbeddingService()
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY not configured"):
            await service.generate_single_embedding("test")
