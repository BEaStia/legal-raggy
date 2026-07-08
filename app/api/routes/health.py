import logging
from pathlib import Path

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

LAWS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "raw" / "laws"


def _check_qdrant() -> dict:
    """Check Qdrant connectivity and collection status."""
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=settings.qdrant_url, timeout=5)
        collections = client.get_collections()
        has_legal_corpus = any(
            c.name == settings.QDRANT_COLLECTION for c in collections.collections
        )
        return {"status": "ok", "url": settings.qdrant_url, "has_legal_corpus": has_legal_corpus}
    except Exception as e:
        logger.warning("Qdrant health check failed: %s", e)
        return {"status": "unavailable", "error": str(e)}


def _check_corpus() -> dict:
    """Check if local laws corpus exists."""
    exists = LAWS_DIR.is_dir()
    file_count = len(list(LAWS_DIR.glob("*.md"))) if exists else 0
    return {"exists": exists, "file_count": file_count, "path": str(LAWS_DIR)}


def _check_llm() -> dict:
    """Check LLM configuration status."""
    return {
        "configured": settings.llm_enabled,
        "provider": settings.LLM_PROVIDER or "none",
        "model": settings.LLM_MODEL or "none",
    }


@router.get("/health")
def health() -> dict:
    """Comprehensive health check."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "qdrant": _check_qdrant(),
        "corpus": _check_corpus(),
        "llm": _check_llm(),
    }
