import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def test_txt_file(fixtures_dir):
    return fixtures_dir / "test.txt"

@pytest.fixture
def test_pdf_file(fixtures_dir):
    return fixtures_dir / "test.pdf"
