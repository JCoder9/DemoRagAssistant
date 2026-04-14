import pytest
from app.services.chunker import TextChunker, Chunk


class TestTextChunker:
    
    def test_real_document_chunking(self, test_txt_file):
        chunker = TextChunker()
        
        with open(test_txt_file, "r") as f:
            text = f.read()
        
        chunks = chunker.chunk_text(text, "test.txt")
        
        assert len(chunks) >= 1
        assert all(chunk.text for chunk in chunks)
        assert all(chunk.source == "test.txt" for chunk in chunks)
    
    def test_chunk_with_overlap(self):
        chunker = TextChunker(chunk_size=50, overlap=10)
        text = "A" * 100
        
        chunks = chunker.chunk_text(text, "test.txt")
        
        assert len(chunks) > 1
        for i in range(len(chunks) - 1):
            assert chunks[i].chunk_id == i
            assert chunks[i + 1].start_char < chunks[i].end_char
    
    def test_sentence_boundary_detection(self):
        chunker = TextChunker(chunk_size=30, overlap=5)
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        
        chunks = chunker.chunk_text(text, "test.txt")
        
        for chunk in chunks:
            assert not chunk.text.startswith(" ")
            assert not chunk.text.endswith(" ")
