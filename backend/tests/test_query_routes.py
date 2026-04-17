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
    
    mock_pipeline.query.assert_called_once_with("What is Python?", 5, None)


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
    mock_pipeline.query.assert_called_once_with("Test question", 5, None)


@patch("app.services.query_service.ChatMemory")
@patch("app.services.query_service.RAGPipeline")
def test_query_endpoint_with_session_id(mock_rag_pipeline_class, mock_chat_memory_class, client):
    mock_memory = Mock()
    mock_memory.get_history = Mock(return_value=[
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous answer"}
    ])
    mock_memory.add_message = Mock()
    mock_chat_memory_class.return_value = mock_memory
    
    mock_pipeline = Mock()
    mock_pipeline.query = AsyncMock(return_value={
        "answer": "Test answer with history",
        "sources": [],
        "context_used": []
    })
    mock_rag_pipeline_class.return_value = mock_pipeline
    
    response = client.post("/api/query", json={
        "question": "Follow-up question",
        "top_k": 5,
        "session_id": "test-session-123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Test answer with history"
    
    mock_memory.get_history.assert_called_once_with("test-session-123")
    
    chat_history = [
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous answer"}
    ]
    mock_pipeline.query.assert_called_once_with("Follow-up question", 5, chat_history)
    
    assert mock_memory.add_message.call_count == 2
    mock_memory.add_message.assert_any_call("test-session-123", "user", "Follow-up question")
    mock_memory.add_message.assert_any_call("test-session-123", "assistant", "Test answer with history")
