"""Dense retriever using Qdrant vector search."""

from qdrant_client import QdrantClient

from app.models.retrieval import DocumentChunk, RetrievedChunk
from app.retrieval.qdrant_store import search_chunks


class DenseRetriever:
    """Dense retrieval over Qdrant-indexed corpus."""

    def __init__(self, client: QdrantClient, collection_name: str | None = None) -> None:
        """Initialize dense retriever.

        Args:
            client: QdrantClient instance.
            collection_name: Collection name (defaults to config).
        """
        self._client = client
        self._collection_name = collection_name

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Search corpus using dense vector similarity.

        Args:
            query: Search query text.
            top_k: Maximum number of results.

        Returns:
            List of RetrievedChunk ordered by similarity score.
        """
        results = search_chunks(
            self._client,
            query,
            top_k=top_k,
            collection_name=self._collection_name,
        )

        return [
            RetrievedChunk(
                chunk=DocumentChunk(
                    chunk_id=r["chunk_id"],
                    document_title=r["document_title"],
                    document_type=r["document_type"],
                    source_path=r["source_path"],
                    heading=r["heading"],
                    text=r["text"],
                    metadata={},
                ),
                score=round(r["score"], 4),
                match_reason="dense_similarity",
            )
            for r in results
        ]
