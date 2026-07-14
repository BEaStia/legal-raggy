"""Application configuration."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LAWS_DIR = PROJECT_ROOT / "data" / "raw" / "laws"


class Settings:
    """Application settings from environment variables."""

    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "legal_corpus")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "e5")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    EMBEDDING_DIMENSION: int = 384

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen/qwen3.7-plus")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.QDRANT_HOST}:{self.QDRANT_PORT}"

    @property
    def llm_enabled(self) -> bool:
        return bool(self.LLM_PROVIDER and self.LLM_API_KEY)


settings = Settings()
