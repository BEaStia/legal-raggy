"""Qdrant vector store for legal corpus."""

import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from app.core.config import settings
from app.models.retrieval import DocumentChunk

_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _chunk_id_to_uuid(chunk_id: str) -> str:
    """Convert an arbitrary chunk_id to a valid UUID string."""
    return str(uuid.uuid5(_NAMESPACE, chunk_id))


def create_collection(client: QdrantClient, collection_name: str | None = None) -> None:
    """Create a Qdrant collection if it doesn't exist.

    Args:
        client: QdrantClient instance.
        collection_name: Collection name (defaults to config).
    """
    name = collection_name or settings.QDRANT_COLLECTION
    if client.collection_exists(name):
        return

    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(
            size=settings.EMBEDDING_DIMENSION,
            distance=Distance.COSINE,
        ),
    )


def collection_has_points(
    client: QdrantClient,
    collection_name: str | None = None,
) -> bool:
    """Check if collection already has indexed points."""
    name = collection_name or settings.QDRANT_COLLECTION
    if not client.collection_exists(name):
        return False
    info = client.get_collection(name)
    return (info.points_count or 0) > 0


def index_chunks(
    client: QdrantClient,
    chunks: list[DocumentChunk],
    collection_name: str | None = None,
) -> int:
    """Index document chunks into Qdrant.

    Skips indexing if collection already has points (idempotent on first run).

    Args:
        client: QdrantClient instance.
        chunks: List of DocumentChunk objects to index.
        collection_name: Collection name (defaults to config).

    Returns:
        Number of chunks indexed (0 if already indexed).
    """
    from app.core.embeddings import embed_texts

    if not chunks:
        return 0

    name = collection_name or settings.QDRANT_COLLECTION
    create_collection(client, name)

    if collection_has_points(client, name):
        return 0

    texts = [c.text for c in chunks]
    vectors = embed_texts(texts)

    points = [
        PointStruct(
            id=_chunk_id_to_uuid(chunk.chunk_id),
            vector=vector,
            payload={
                "chunk_id": chunk.chunk_id,
                "document_title": chunk.document_title,
                "document_type": chunk.document_type,
                "source_path": chunk.source_path,
                "heading": chunk.heading,
                "text": chunk.text,
                "metadata": chunk.metadata,
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]

    client.upsert(collection_name=name, points=points)
    return len(points)


def search_chunks(
    client: QdrantClient,
    query: str,
    top_k: int = 5,
    collection_name: str | None = None,
) -> list[dict]:
    """Search for chunks similar to the query.

    Args:
        client: QdrantClient instance.
        query: Search query text.
        top_k: Number of results to return.
        collection_name: Collection name (defaults to config).

    Returns:
        List of dicts with chunk data and score.
    """
    from app.core.embeddings import embed_text

    name = collection_name or settings.QDRANT_COLLECTION
    query_vector = embed_text(query)

    results = client.query_points(
        collection_name=name,
        query=query_vector,
        limit=top_k,
    )

    return [
        {
            "chunk_id": (hit.payload or {}).get("chunk_id", str(hit.id)),
            "score": hit.score,
            "document_title": (hit.payload or {}).get("document_title"),
            "document_type": (hit.payload or {}).get("document_type"),
            "source_path": (hit.payload or {}).get("source_path"),
            "heading": (hit.payload or {}).get("heading"),
            "text": (hit.payload or {}).get("text"),
        }
        for hit in results.points
    ]
