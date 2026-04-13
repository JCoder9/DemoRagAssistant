import pymupdf as fitz
from fastapi import UploadFile, HTTPException
from pathlib import Path

class DocumentLoader:
    SUPPORTED_TYPES = {
        "application/pdf": ".pdf",
        "text/plain": ".txt"
    }
    
    async def load_document(self, file: UploadFile) -> str:
        if file.content_type not in self.SUPPORTED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: PDF, TXT"
            )
        
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if file.content_type == "application/pdf":
            return self._extract_pdf_text(content)
        else:
            return self._extract_txt_text(content)
    
    def _extract_pdf_text(self, content: bytes) -> str:
        try:
            pdf_document = fitz.open(stream=content, filetype="pdf")
            text_content = []
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text_content.append(page.get_text())
            
            pdf_document.close()
            extracted_text = "\n\n".join(text_content).strip()
            
            if not extracted_text:
                raise HTTPException(status_code=400, detail="No text found in PDF")
            
            return extracted_text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")
    
    def _extract_txt_text(self, content: bytes) -> str:
        try:
            text = content.decode("utf-8").strip()
            if not text:
                raise HTTPException(status_code=400, detail="Empty text file")
            return text
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Invalid text encoding")
