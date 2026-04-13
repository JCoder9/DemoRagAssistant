import pytest
from io import BytesIO
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.services.document_loader import DocumentLoader


class TestDocumentLoader:
    
    @pytest.mark.asyncio
    async def test_load_text_file(self, test_txt_file):
        loader = DocumentLoader()
        
        with open(test_txt_file, "rb") as f:
            content = f.read()
        
        file = UploadFile(
            filename="test.txt",
            file=BytesIO(content),
            headers={"content-type": "text/plain"}
        )
        
        result = await loader.load_document(file)
        assert len(result) > 0
        assert "John Doe" in result
        assert "Jane Doe" in result
    
    @pytest.mark.asyncio
    async def test_load_pdf_file(self, test_pdf_file):
        loader = DocumentLoader()
        
        with open(test_pdf_file, "rb") as f:
            content = f.read()
        
        file = UploadFile(
            filename="test.pdf",
            file=BytesIO(content),
            headers={"content-type": "application/pdf"}
        )
        
        result = await loader.load_document(file)
        assert len(result) > 0
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_empty_file_raises_error(self):
        loader = DocumentLoader()
        file = UploadFile(
            filename="empty.txt",
            file=BytesIO(b""),
            headers={"content-type": "text/plain"}
        )
        
        with pytest.raises(HTTPException) as exc:
            await loader.load_document(file)
        assert exc.value.status_code == 400
        assert "Empty file" in exc.value.detail
    
    @pytest.mark.asyncio
    async def test_whitespace_only_file_raises_error(self):
        loader = DocumentLoader()
        file = UploadFile(
            filename="whitespace.txt",
            file=BytesIO(b"   \n\n   \t  "),
            headers={"content-type": "text/plain"}
        )
        
        with pytest.raises(HTTPException) as exc:
            await loader.load_document(file)
        assert exc.value.status_code == 400
        assert "Empty text file" in exc.value.detail
    
    @pytest.mark.asyncio
    async def test_unsupported_file_type(self):
        loader = DocumentLoader()
        file = UploadFile(
            filename="image.jpg",
            file=BytesIO(b"fake image data"),
            headers={"content-type": "image/jpeg"}
        )
        
        with pytest.raises(HTTPException) as exc:
            await loader.load_document(file)
        assert exc.value.status_code == 400
        assert "Unsupported file type" in exc.value.detail
    
    @pytest.mark.asyncio
    async def test_invalid_text_encoding(self):
        loader = DocumentLoader()
        file = UploadFile(
            filename="invalid.txt",
            file=BytesIO(b"\x80\x81\x82\x83"),
            headers={"content-type": "text/plain"}
        )
        
        with pytest.raises(HTTPException) as exc:
            await loader.load_document(file)
        assert exc.value.status_code == 400
        assert "Invalid text encoding" in exc.value.detail
    
    @pytest.mark.asyncio
    async def test_invalid_pdf_raises_error(self):
        loader = DocumentLoader()
        file = UploadFile(
            filename="fake.pdf",
            file=BytesIO(b"This is not a real PDF file"),
            headers={"content-type": "application/pdf"}
        )
        
        with pytest.raises(HTTPException) as exc:
            await loader.load_document(file)
        assert exc.value.status_code == 400
        assert "Invalid PDF" in exc.value.detail
