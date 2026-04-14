import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from app.services.vector_store import VectorStore


class TestVectorStore:
    
    @pytest.fixture
    def temp_store_path(self):
        temp_dir = tempfile.mkdtemp()
        yield str(Path(temp_dir) / "test_vector_store")
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_embeddings(self):
        return [
            [0.1] * 1536,
            [0.2] * 1536,
            [0.3] * 1536,
        ]
    
    @pytest.fixture
    def sample_texts(self):
        return [
            "Machine learning is a subset of AI",
            "Python is a programming language",
            "FAISS is a vector similarity search library",
        ]
    
    def test_add_and_search_documents(self, temp_store_path, sample_texts, sample_embeddings):
        store = VectorStore(index_path=temp_store_path)
        
        metadata = [{"source": "doc1"}, {"source": "doc2"}, {"source": "doc3"}]
        store.add_documents(sample_texts, sample_embeddings, metadata)
        
        assert store.get_document_count() == 3
        
        query_embedding = [0.15] * 1536
        results = store.search(query_embedding, top_k=2)
        
        assert len(results) == 2
        assert "text" in results[0]
        assert "score" in results[0]
        assert "metadata" in results[0]
    
    def test_save_and_load_index(self, temp_store_path, sample_texts, sample_embeddings):
        store1 = VectorStore(index_path=temp_store_path)
        store1.add_documents(sample_texts, sample_embeddings)
        store1.save_index()
        
        store2 = VectorStore(index_path=temp_store_path)
        assert store2.get_document_count() == 3
        
        query_embedding = [0.1] * 1536
        results = store2.search(query_embedding, top_k=1)
        
        assert len(results) == 1
        assert results[0]["text"] in sample_texts
    
    def test_search_empty_index(self, temp_store_path):
        store = VectorStore(index_path=temp_store_path)
        
        query_embedding = [0.1] * 1536
        results = store.search(query_embedding)
        
        assert results == []
    
    def test_dimension_mismatch_error(self, temp_store_path):
        store = VectorStore(dimension=1536, index_path=temp_store_path)
        
        wrong_embeddings = [[0.1] * 512]
        
        with pytest.raises(ValueError, match="does not match index dimension"):
            store.add_documents(["test"], wrong_embeddings)
    
    def test_clear_index(self, temp_store_path, sample_texts, sample_embeddings):
        store = VectorStore(index_path=temp_store_path)
        store.add_documents(sample_texts, sample_embeddings)
        
        assert store.get_document_count() == 3
        
        store.clear()
        
        assert store.get_document_count() == 0
