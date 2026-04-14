import os
from app.config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K,
    DEFAULT_ALLOWED_ORIGINS,
    DEFAULT_EMBEDDING_MODEL,
)

class Settings:
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", DEFAULT_CHUNK_SIZE))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP))
        self.TOP_K = int(os.getenv("TOP_K", DEFAULT_TOP_K))
        self.ALLOWED_ORIGINS = os.getenv(
            "ALLOWED_ORIGINS", ",".join(DEFAULT_ALLOWED_ORIGINS)
        ).split(",")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)

settings = Settings()
