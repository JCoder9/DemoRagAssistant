import pytest
from io import BytesIO


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_real_text_file(client, test_txt_file):
    with open(test_txt_file, "rb") as f:
        files = {
            "file": ("test.txt", f, "text/plain")
        }
        response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert "text" in data
    assert "John Doe" in data["text"]
    assert data["char_count"] > 0
    assert "chunks" in data
    assert "chunk_count" in data
    assert data["chunk_count"] > 0
    assert len(data["chunks"]) == data["chunk_count"]


def test_upload_real_pdf_file(client, test_pdf_file):
    with open(test_pdf_file, "rb") as f:
        files = {
            "file": ("test.pdf", f, "application/pdf")
        }
        response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert "text" in data
    assert len(data["text"]) > 0
    assert data["char_count"] > 0
    assert "chunks" in data
    assert "chunk_count" in data
    assert data["chunk_count"] > 0
