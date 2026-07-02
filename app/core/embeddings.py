"""Embedding service using sentence-transformers."""

from sentence_transformers import SentenceTransformer

from app.core.config import settings

_MODEL: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model."""
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _MODEL


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (lists of floats).
    """
    model = _get_model()
    return model.encode(texts, normalize_embeddings=True).tolist()


def embed_text(text: str) -> list[float]:
    """Generate embedding for a single text.

    Args:
        text: Text string to embed.

    Returns:
        Embedding vector (list of floats).
    """
    return embed_texts([text])[0]
