from fastapi import UploadFile
from app.services.document_loader import DocumentLoader
from app.services.chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

class UploadService:
    def __init__(self):
        self.document_loader = DocumentLoader()
        self.chunker = TextChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    
    async def process_upload(self, file: UploadFile):
        extracted_text = await self.document_loader.load_document(file)
        chunks = self.chunker.chunk_text(extracted_text, file.filename)
        
        if not chunks:
            return {
                "filename": file.filename,
                "char_count": len(extracted_text),
                "chunk_count": 0,
                "message": "No content to process"
            }
        
        texts = [chunk.text for chunk in chunks]
        metadata = [
            {
                "source": file.filename,
                "chunk_id": chunk.chunk_id,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char
            }
            for chunk in chunks
        ]
        
        embeddings_data = await self.embedding_service.generate_embeddings(texts, metadata)
        
        embeddings = [item["embedding"] for item in embeddings_data]
        
        self.vector_store.add_documents(texts, embeddings, metadata)
        self.vector_store.save_index()
        
        return {
            "filename": file.filename,
            "char_count": len(extracted_text),
            "chunk_count": len(chunks),
            "message": f"Successfully processed and stored {len(chunks)} chunks"
        }
