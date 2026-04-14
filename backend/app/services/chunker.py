from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Chunk:
    text: str
    chunk_id: int
    source: str
    start_char: int
    end_char: int

class TextChunker:
    def __init__(self, chunk_size: int = 2000, overlap: int = 400):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, source: str) -> List[Chunk]:
        if not text or not text.strip():
            return []
        
        chunks = []
        text_length = len(text)
        start = 0
        chunk_id = 0
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            if end < text_length:
                end = self._find_sentence_boundary(text, end)
            
            # Ensure we always make progress (avoid infinite loop)
            if end <= start:
                end = min(start + self.chunk_size, text_length)
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append(Chunk(
                    text=chunk_text,
                    chunk_id=chunk_id,
                    source=source,
                    start_char=start,
                    end_char=end
                ))
                chunk_id += 1
            
            # Move start forward, ensuring progress
            next_start = end - self.overlap
            if next_start <= start:
                next_start = end
            
            start = next_start
            if start >= text_length:
                break
        
        return chunks
    
    def _find_sentence_boundary(self, text: str, position: int) -> int:
        search_window = 200
        start_search = max(0, position - search_window)
        end_search = min(len(text), position + search_window)
        
        search_text = text[start_search:end_search]
        relative_pos = position - start_search
        
        sentence_endings = ['. ', '.\n', '! ', '!\n', '? ', '?\n']
        
        best_pos = None
        min_distance = float('inf')
        
        for ending in sentence_endings:
            idx = search_text.rfind(ending, 0, relative_pos + len(ending))
            if idx != -1:
                distance = abs(relative_pos - idx)
                if distance < min_distance:
                    min_distance = distance
                    best_pos = idx + len(ending)
        
        if best_pos is not None:
            return start_search + best_pos
        
        space_idx = search_text.rfind(' ', 0, relative_pos)
        if space_idx != -1:
            return start_search + space_idx + 1
        
        return position
    
    def chunk_to_dict(self, chunk: Chunk) -> Dict:
        return {
            "text": chunk.text,
            "chunk_id": chunk.chunk_id,
            "source": chunk.source,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char
        }
