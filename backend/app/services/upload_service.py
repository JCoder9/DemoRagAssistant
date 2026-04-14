from fastapi import UploadFile
from app.services.document_loader import DocumentLoader
from app.services.chunker import TextChunker

class UploadService:
    def __init__(self):
        self.document_loader = DocumentLoader()
        self.chunker = TextChunker()
    
    async def process_upload(self, file: UploadFile):
        extracted_text = await self.document_loader.load_document(file)
        chunks = self.chunker.chunk_text(extracted_text, file.filename)
        
        return {
            "filename": file.filename,
            "text": extracted_text,
            "char_count": len(extracted_text),
            "chunks": [self.chunker.chunk_to_dict(chunk) for chunk in chunks],
            "chunk_count": len(chunks)
        }
