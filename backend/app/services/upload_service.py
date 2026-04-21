from fastapi import UploadFile, HTTPException
from app.services.document_loader import DocumentLoader
from app.services.chunker import TextChunker
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)

class UploadService:
    def __init__(self):
        self.document_loader = DocumentLoader()
        self.chunker = TextChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    
    async def process_upload(self, file: UploadFile):
        # Check if file already exists
        if self.vector_store.has_document(file.filename):
            raise HTTPException(
                status_code=409,
                detail=f"File '{file.filename}' has already been uploaded. Please upload a different file or clear existing documents first."
            )
        
        extracted_text = await self.document_loader.load_document(file)
        
        # Log extracted text
        print("\n" + "="*80)
        print(f"EXTRACTED TEXT FROM: {file.filename}")
        print("="*80)
        print(f"Total characters: {len(extracted_text)}")
        print("-"*80)
        print(extracted_text)
        print("="*80 + "\n")
        
        chunks = self.chunker.chunk_text(extracted_text, file.filename)
        
        if not chunks:
            return {
                "filename": file.filename,
                "char_count": len(extracted_text),
                "chunk_count": 0,
                "message": "No content to process"
            }
        
        # Log chunks
        print("\n" + "="*80)
        print(f"CHUNKS CREATED FROM: {file.filename}")
        print("="*80)
        print(f"Total chunks: {len(chunks)}")
        print("-"*80)
        for i, chunk in enumerate(chunks, 1):
            print(f"\nCHUNK #{i}:")
            print(f"  ID: {chunk.chunk_id}")
            print(f"  Characters: {chunk.start_char} - {chunk.end_char} (length: {len(chunk.text)})")
            print(f"  Text preview (first 200 chars):")
            print(f"  {chunk.text[:200]}...")
            print(f"  Full text:")
            print(f"  {chunk.text}")
            print("-"*80)
        print("="*80 + "\n")
        
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
