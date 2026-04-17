import pytest
from unittest.mock import AsyncMock, Mock, patch


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.services.upload_service.EmbeddingService")
@patch("app.services.upload_service.VectorStore")
def test_upload_real_text_file(mock_vector_store_class, mock_embedding_service_class, client, test_txt_file, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    
    mock_embedding_service = Mock()
    mock_embedding_service.generate_embeddings = AsyncMock(return_value=[
        {"embedding": [0.1] * 1536, "text": "chunk1", "index": 0}
    ])
    mock_embedding_service_class.return_value = mock_embedding_service
    
    mock_vector_store = Mock()
    mock_vector_store.add_documents = Mock()
    mock_vector_store.save_index = Mock()
    mock_vector_store_class.return_value = mock_vector_store
    
    with open(test_txt_file, "rb") as f:
        files = {
            "file": ("test.txt", f, "text/plain")
        }
        response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["char_count"] > 0
    assert data["chunk_count"] > 0
    assert "message" in data
    assert "Successfully processed" in data["message"]
    
    mock_embedding_service.generate_embeddings.assert_called_once()
    mock_vector_store.add_documents.assert_called_once()
    mock_vector_store.save_index.assert_called_once()


@patch("app.services.upload_service.EmbeddingService")
@patch("app.services.upload_service.VectorStore")
def test_upload_real_pdf_file(mock_vector_store_class, mock_embedding_service_class, client, test_pdf_file, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    
    mock_embedding_service = Mock()
    mock_embedding_service.generate_embeddings = AsyncMock(return_value=[
        {"embedding": [0.1] * 1536, "text": "chunk1", "index": 0}
    ])
    mock_embedding_service_class.return_value = mock_embedding_service
    
    mock_vector_store = Mock()
    mock_vector_store.add_documents = Mock()
    mock_vector_store.save_index = Mock()
    mock_vector_store_class.return_value = mock_vector_store
    
    with open(test_pdf_file, "rb") as f:
        files = {
            "file": ("test.pdf", f, "application/pdf")
        }
        response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["char_count"] > 0
    assert data["chunk_count"] > 0
    assert "message" in data
