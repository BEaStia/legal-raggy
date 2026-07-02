"""Hybrid retriever combining keyword and dense retrieval."""

from collections import defaultdict

from app.models.retrieval import DocumentChunk, RetrievedChunk
from app.retrieval.dense import DenseRetriever
from app.retrieval.keyword import KeywordRetriever


class HybridRetriever:
    """Combines keyword and dense retrieval with Reciprocal Rank Fusion.

    RRF is robust to different score scales and produces stable rankings.
    """

    def __init__(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
        keyword_weight: float = 0.5,
        dense_weight: float = 0.5,
        k: int = 60,
    ) -> None:
        """Initialize hybrid retriever.

        Args:
            keyword_retriever: KeywordRetriever instance.
            dense_retriever: DenseRetriever instance.
            keyword_weight: Weight for keyword scores in final ranking.
            dense_weight: Weight for dense scores in final ranking.
            k: RRF constant (default 60, standard value).
        """
        self._keyword = keyword_retriever
        self._dense = dense_retriever
        self._kw_weight = keyword_weight
        self._dense_weight = dense_weight
        self._k = k

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Search using hybrid keyword + dense retrieval.

        Uses Reciprocal Rank Fusion to combine rankings from both retrievers.

        Args:
            query: Search query text.
            top_k: Maximum number of results.

        Returns:
            List of RetrievedChunk ordered by hybrid score.
        """
        kw_results = self._keyword.search(query, top_k=top_k * 3)
        dense_results = self._dense.search(query, top_k=top_k * 3)

        rrf_scores: dict[str, float] = defaultdict(float)
        chunk_map: dict[str, DocumentChunk] = {}
        kw_reasons: dict[str, str | None] = {}

        for rank, result in enumerate(kw_results, 1):
            cid = result.chunk.chunk_id
            rrf_scores[cid] += self._kw_weight / (self._k + rank)
            chunk_map[cid] = result.chunk
            kw_reasons[cid] = result.match_reason

        for rank, result in enumerate(dense_results, 1):
            cid = result.chunk.chunk_id
            rrf_scores[cid] += self._dense_weight / (self._k + rank)
            if cid not in chunk_map:
                chunk_map[cid] = result.chunk

        ranked = sorted(rrf_scores.items(), key=lambda x: -x[1])

        return [
            RetrievedChunk(
                chunk=chunk_map[cid],
                score=round(score, 6),
                match_reason=kw_reasons.get(cid, "dense_similarity"),
            )
            for cid, score in ranked[:top_k]
        ]
