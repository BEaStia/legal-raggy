"""Tests for hybrid keyword + dense retrieval."""

from pathlib import Path

import pytest
from qdrant_client import QdrantClient

from app.ingestion.chunking import load_corpus
from app.models.retrieval import DocumentChunk
from app.retrieval.dense import DenseRetriever
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.keyword import KeywordRetriever
from app.retrieval.qdrant_store import index_chunks


@pytest.fixture
def qdrant_client() -> QdrantClient:
    return QdrantClient(":memory:")


@pytest.fixture
def test_chunks() -> list[DocumentChunk]:
    return [
        DocumentChunk(
            chunk_id="550e8400-e29b-41d4-a716-446655440001",
            document_title="152-ФЗ",
            document_type="federal_law",
            source_path="laws/152fz.md",
            heading="Персональные данные",
            text=(
                "Персональные данные — любая информация, относящаяся "
                "к прямо или косвенно определённому физическому лицу. "
                "Обработка персональных данных требует согласия субъекта."
            ),
            metadata={},
        ),
        DocumentChunk(
            chunk_id="550e8400-e29b-41d4-a716-446655440002",
            document_title="63-ФЗ",
            document_type="federal_law",
            source_path="laws/63fz.md",
            heading="Электронная подпись",
            text=(
                "Электронная подпись — информация в электронной форме, "
                "присоединённая к другой информации. "
                "Усиленная квалифицированная электронная подпись "
                "признаётся равнозначной собственноручной."
            ),
            metadata={},
        ),
        DocumentChunk(
            chunk_id="550e8400-e29b-41d4-a716-446655440003",
            document_title="98-ФЗ",
            document_type="federal_law",
            source_path="laws/98fz.md",
            heading="Коммерческая тайна",
            text=(
                "Коммерческая тайна — режим конфиденциальности информации. "
                "Обладатель информации должен принять меры "
                "по охране конфиденциальности."
            ),
            metadata={},
        ),
    ]


@pytest.fixture
def keyword_retriever(test_chunks: list[DocumentChunk]) -> KeywordRetriever:
    r = KeywordRetriever()
    r.load_chunks(test_chunks)
    return r


@pytest.fixture
def dense_retriever(
    qdrant_client: QdrantClient,
    test_chunks: list[DocumentChunk],
) -> DenseRetriever:
    index_chunks(qdrant_client, test_chunks, "test_hybrid")
    return DenseRetriever(qdrant_client, "test_hybrid")


class TestHybridRetriever:
    def test_returns_results(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
    ) -> None:
        hybrid = HybridRetriever(keyword_retriever, dense_retriever)
        results = hybrid.search("персональные данные", top_k=3)
        assert len(results) >= 1

    def test_top_result_is_relevant(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
    ) -> None:
        hybrid = HybridRetriever(keyword_retriever, dense_retriever)
        results = hybrid.search("персональные данные", top_k=3)
        assert results[0].chunk.document_title == "152-ФЗ"

    def test_respects_top_k(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
    ) -> None:
        hybrid = HybridRetriever(keyword_retriever, dense_retriever)
        results = hybrid.search("данные", top_k=1)
        assert len(results) == 1

    def test_scores_descending(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
    ) -> None:
        hybrid = HybridRetriever(keyword_retriever, dense_retriever)
        results = hybrid.search("данные", top_k=5)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_deduplicates_results(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
    ) -> None:
        hybrid = HybridRetriever(keyword_retriever, dense_retriever)
        results = hybrid.search("персональные данные", top_k=5)
        chunk_ids = [r.chunk.chunk_id for r in results]
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_preserves_provenance(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
    ) -> None:
        hybrid = HybridRetriever(keyword_retriever, dense_retriever)
        results = hybrid.search("персональные данные", top_k=3)
        chunk = results[0].chunk
        assert chunk.source_path == "laws/152fz.md"
        assert chunk.heading == "Персональные данные"

    def test_electronic_signature(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
    ) -> None:
        hybrid = HybridRetriever(keyword_retriever, dense_retriever)
        results = hybrid.search("электронная подпись", top_k=3)
        assert results[0].chunk.document_title == "63-ФЗ"

    def test_commercial_secret(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
    ) -> None:
        hybrid = HybridRetriever(keyword_retriever, dense_retriever)
        results = hybrid.search("коммерческая тайна", top_k=3)
        assert results[0].chunk.document_title == "98-ФЗ"

    def test_custom_weights(
        self,
        keyword_retriever: KeywordRetriever,
        dense_retriever: DenseRetriever,
    ) -> None:
        """Higher keyword weight should prioritize keyword matches."""
        hybrid_kw = HybridRetriever(
            keyword_retriever, dense_retriever,
            keyword_weight=0.9, dense_weight=0.1,
        )
        hybrid_dense = HybridRetriever(
            keyword_retriever, dense_retriever,
            keyword_weight=0.1, dense_weight=0.9,
        )
        results_kw = hybrid_kw.search("персональные данные", top_k=3)
        results_dense = hybrid_dense.search("персональные данные", top_k=3)
        assert results_kw[0].chunk.document_title == "152-ФЗ"
        assert results_dense[0].chunk.document_title == "152-ФЗ"

    def test_loads_from_real_corpus(
        self,
        qdrant_client: QdrantClient,
    ) -> None:
        """Test hybrid search over the actual legal corpus."""
        project_root = Path(__file__).parent.parent
        laws_dir = project_root / "data" / "raw" / "laws"
        if laws_dir.is_dir():
            chunks = load_corpus(laws_dir)
            assert len(chunks) > 0

            kw = KeywordRetriever()
            kw.load_chunks(chunks)

            index_chunks(qdrant_client, chunks, "real_hybrid")
            dense = DenseRetriever(qdrant_client, "real_hybrid")

            hybrid = HybridRetriever(kw, dense)
            results = hybrid.search(
                "требования к защите персональных данных",
                top_k=5,
            )
            assert len(results) > 0
            assert any("152" in r.chunk.document_title for r in results)
