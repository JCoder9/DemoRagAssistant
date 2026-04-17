import pytest
from unittest.mock import AsyncMock, Mock, patch


@pytest.fixture(autouse=True)
def mock_openai_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")


@patch("app.services.query_service.RAGPipeline")
def test_query_endpoint_with_results(mock_rag_pipeline_class, client):
    mock_pipeline = Mock()
    mock_pipeline.query = AsyncMock(return_value={
        "answer": "Python is a high-level programming language.",
        "sources": [
            {
                "text": "Python is a programming language",
                "score": 0.1,
                "metadata": {"source": "doc1.pdf"}
            }
        ],
        "context_used": ["Python is a programming language"]
    })
    mock_rag_pipeline_class.return_value = mock_pipeline
    
    response = client.post("/api/query", json={
        "question": "What is Python?",
        "top_k": 5
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert data["answer"] == "Python is a high-level programming language."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["text"] == "Python is a programming language"
    
    mock_pipeline.query.assert_called_once_with("What is Python?", 5)


@patch("app.services.query_service.RAGPipeline")
def test_query_endpoint_no_results(mock_rag_pipeline_class, client):
    mock_pipeline = Mock()
    mock_pipeline.query = AsyncMock(return_value={
        "answer": "I don't have enough context to answer this question.",
        "sources": [],
        "context_used": []
    })
    mock_rag_pipeline_class.return_value = mock_pipeline
    
    response = client.post("/api/query", json={
        "question": "What is quantum computing?",
        "top_k": 5
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert data["sources"] == []


@patch("app.services.query_service.RAGPipeline")
def test_query_endpoint_default_top_k(mock_rag_pipeline_class, client):
    mock_pipeline = Mock()
    mock_pipeline.query = AsyncMock(return_value={
        "answer": "Test answer",
        "sources": [],
        "context_used": []
    })
    mock_rag_pipeline_class.return_value = mock_pipeline
    
    response = client.post("/api/query", json={
        "question": "Test question"
    })
    
    assert response.status_code == 200
    mock_pipeline.query.assert_called_once_with("Test question", 5)
