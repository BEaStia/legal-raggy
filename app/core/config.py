"""Application configuration."""

import os


class Settings:
    """Application settings from environment variables."""

    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "legal_corpus")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "e5")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    EMBEDDING_DIMENSION: int = 384

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"


settings = Settings()
