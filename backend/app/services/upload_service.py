from fastapi import UploadFile
from app.services.document_loader import DocumentLoader

class UploadService:
    def __init__(self):
        self.document_loader = DocumentLoader()
    
    async def process_upload(self, file: UploadFile):
        extracted_text = await self.document_loader.load_document(file)
        
        return {
            "filename": file.filename,
            "text": extracted_text,
            "char_count": len(extracted_text)
        }
