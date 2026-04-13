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


def test_upload_empty_file(client):
    files = {
        "file": ("empty.txt", BytesIO(b""), "text/plain")
    }
    
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400
    assert "Empty file" in response.json()["detail"]


def test_upload_unsupported_file_type(client):
    files = {
        "file": ("image.jpg", BytesIO(b"fake image"), "image/jpeg")
    }
    
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_whitespace_only_text(client):
    files = {
        "file": ("whitespace.txt", BytesIO(b"   \n\n   "), "text/plain")
    }
    
    response = client.post("/api/upload", files=files)
    assert response.status_code == 400


def test_upload_without_file(client):
    response = client.post("/api/upload")
    assert response.status_code == 422
