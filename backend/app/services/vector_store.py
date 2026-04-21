import os
from typing import List, Dict, Tuple
from pathlib import Path
import pickle
import numpy as np
import faiss
from app.settings import settings


class VectorStore:
    def __init__(self, dimension: int = None, index_path: str = None):
        self.dimension = dimension or settings.EMBEDDING_DIM
        self.index_path = index_path or settings.VECTOR_STORE_PATH
        self.index = None
        self.documents = []
        self._initialize_index()
    
    def _initialize_index(self):
        if self._load_index():
            return
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
    
    def add_documents(
        self, 
        texts: List[str], 
        embeddings: List[List[float]], 
        metadata: List[Dict] = None
    ) -> None:
        if not texts or not embeddings:
            return
        
        if len(texts) != len(embeddings):
            raise ValueError("texts and embeddings must have the same length")
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        if embeddings_array.shape[1] != self.dimension: #check embedding_array number of columns matches index dimension
            raise ValueError(f"Embedding dimension {embeddings_array.shape[1]} does not match index dimension {self.dimension}")
        
        self.index.add(embeddings_array)
        
        for i, text in enumerate(texts):
            doc = {
                "text": text,
                "index": len(self.documents),
                "embedding": embeddings[i]
            }
            if metadata and i < len(metadata):
                doc["metadata"] = metadata[i]
            
            self.documents.append(doc)
    
    def search(
        self, 
        query_embedding: List[float], 
        top_k: int = None
    ) -> List[Dict]:
        if not self.index or self.index.ntotal == 0:
            return []
        
        k = min(top_k or settings.TOP_K, self.index.ntotal)
        
        query_array = np.array([query_embedding], dtype=np.float32)
        
        if query_array.shape[1] != self.dimension:
            raise ValueError(f"Query embedding dimension {query_array.shape[1]} does not match index dimension {self.dimension}")
        
        distances, indices = self.index.search(query_array, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                result = {
                    "text": self.documents[idx]["text"],
                    "score": float(distances[0][i]),
                    "index": int(idx),
                }
                if "metadata" in self.documents[idx]:
                    result["metadata"] = self.documents[idx]["metadata"]
                
                results.append(result)
        
        return results
    
    def save_index(self) -> None:
        path = Path(self.index_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, f"{self.index_path}.faiss")
        
        with open(f"{self.index_path}.pkl", "wb") as f:
            pickle.dump(self.documents, f)
    
    def _load_index(self) -> bool:
        faiss_path = f"{self.index_path}.faiss"
        pkl_path = f"{self.index_path}.pkl"
        
        if not os.path.exists(faiss_path) or not os.path.exists(pkl_path):
            return False
        
        try:
            self.index = faiss.read_index(faiss_path)
            
            with open(pkl_path, "rb") as f:
                self.documents = pickle.load(f)
            
            return True
        except Exception:
            return False
    
    def clear(self) -> None:
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
    
    def get_document_count(self) -> int:
        return len(self.documents)
    
    def has_document(self, filename: str) -> bool:
        """Check if a document with the given filename already exists."""
        for doc in self.documents:
            if doc.get("metadata", {}).get("source") == filename:
                return True
        return False
    
    def get_uploaded_files(self) -> List[str]:
        """Get list of unique filenames that have been uploaded."""
        filenames = set()
        for doc in self.documents:
            source = doc.get("metadata", {}).get("source")
            if source:
                filenames.add(source)
        return sorted(list(filenames))
    
    def remove_document(self, filename: str) -> int:
        """Remove all chunks from a specific filename and rebuild index. Returns number of chunks removed."""
        # Find documents to keep and extract their embeddings BEFORE rebuilding
        remaining_docs = []
        removed_count = 0
        
        for doc in self.documents:
            if doc.get("metadata", {}).get("source") == filename:
                removed_count += 1
            else:
                # Extract embedding now (either from doc or from FAISS index)
                if "embedding" in doc:
                    embedding = doc["embedding"]
                else:
                    # Reconstruct embedding from FAISS index for old documents
                    # that were saved before embedding storage was added
                    doc_idx = doc.get("index", -1)
                    if doc_idx >= 0 and doc_idx < self.index.ntotal:
                        embedding = self.index.reconstruct(int(doc_idx)).tolist()
                    else:
                        # Cannot reconstruct, skip this document
                        continue
                
                remaining_docs.append({
                    "text": doc["text"],
                    "embedding": embedding,
                    "metadata": doc.get("metadata")
                })
        
        if removed_count == 0:
            return 0
        
        # Rebuild index with remaining documents
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        
        if remaining_docs:
            # Extract embeddings and texts from remaining documents
            embeddings = [doc["embedding"] for doc in remaining_docs]
            texts = [doc["text"] for doc in remaining_docs]
            metadata_list = [doc.get("metadata") for doc in remaining_docs]
            
            # Re-add to index
            embeddings_array = np.array(embeddings, dtype=np.float32)
            self.index.add(embeddings_array)
            
            # Rebuild documents list with updated indices
            for i, doc in enumerate(remaining_docs):
                new_doc = {
                    "text": doc["text"],
                    "index": i,
                    "embedding": doc["embedding"]
                }
                if doc.get("metadata"):
                    new_doc["metadata"] = doc["metadata"]
                self.documents.append(new_doc)
        
        return removed_count
