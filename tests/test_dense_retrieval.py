"""Tests for dense retrieval with Qdrant."""

from pathlib import Path

import pytest
from qdrant_client import QdrantClient

from app.ingestion.chunking import load_corpus
from app.models.retrieval import DocumentChunk
from app.retrieval.dense import DenseRetriever
from app.retrieval.qdrant_store import create_collection, index_chunks, search_chunks


@pytest.fixture
def qdrant_client() -> QdrantClient:
    """In-memory Qdrant client for testing."""
    return QdrantClient(":memory:")


@pytest.fixture
def test_chunks() -> list[DocumentChunk]:
    """Test chunks with known content."""
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
            metadata={"domain": "personal_data"},
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
            metadata={"domain": "electronic_signature"},
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
            metadata={"domain": "commercial_secret"},
        ),
    ]


class TestQdrantStore:
    def test_creates_collection(self, qdrant_client: QdrantClient) -> None:
        create_collection(qdrant_client, "test_collection")
        assert qdrant_client.collection_exists("test_collection")

    def test_idempotent_collection_creation(self, qdrant_client: QdrantClient) -> None:
        create_collection(qdrant_client, "test_collection")
        create_collection(qdrant_client, "test_collection")
        assert qdrant_client.collection_exists("test_collection")

    def test_indexes_chunks(
        self, qdrant_client: QdrantClient, test_chunks: list[DocumentChunk]
    ) -> None:
        count = index_chunks(qdrant_client, test_chunks, "test_collection")
        assert count == 3

    def test_search_returns_results(
        self, qdrant_client: QdrantClient, test_chunks: list[DocumentChunk]
    ) -> None:
        index_chunks(qdrant_client, test_chunks, "test_collection")
        results = search_chunks(
            qdrant_client,
            "персональные данные",
            top_k=3,
            collection_name="test_collection",
        )
        assert len(results) >= 1
        assert results[0]["document_title"] == "152-ФЗ"

    def test_search_scores_descending(
        self, qdrant_client: QdrantClient, test_chunks: list[DocumentChunk]
    ) -> None:
        index_chunks(qdrant_client, test_chunks, "test_collection")
        results = search_chunks(qdrant_client, "данные", top_k=5, collection_name="test_collection")
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_empty_corpus(self, qdrant_client: QdrantClient) -> None:
        create_collection(qdrant_client, "empty_collection")
        results = search_chunks(qdrant_client, "query", top_k=5, collection_name="empty_collection")
        assert results == []


class TestDenseRetriever:
    def test_search_returns_retrieved_chunks(
        self, qdrant_client: QdrantClient, test_chunks: list[DocumentChunk]
    ) -> None:
        index_chunks(qdrant_client, test_chunks, "test_collection")
        retriever = DenseRetriever(qdrant_client, "test_collection")
        results = retriever.search("персональные данные", top_k=3)
        assert len(results) >= 1
        assert results[0].chunk.document_title == "152-ФЗ"
        assert results[0].score > 0
        assert results[0].match_reason == "dense_similarity"

    def test_search_respects_top_k(
        self, qdrant_client: QdrantClient, test_chunks: list[DocumentChunk]
    ) -> None:
        index_chunks(qdrant_client, test_chunks, "test_collection")
        retriever = DenseRetriever(qdrant_client, "test_collection")
        results = retriever.search("данные", top_k=1)
        assert len(results) == 1

    def test_search_electronic_signature(
        self, qdrant_client: QdrantClient, test_chunks: list[DocumentChunk]
    ) -> None:
        index_chunks(qdrant_client, test_chunks, "test_collection")
        retriever = DenseRetriever(qdrant_client, "test_collection")
        results = retriever.search("электронная подпись", top_k=3)
        assert len(results) >= 1
        assert results[0].chunk.document_title == "63-ФЗ"

    def test_search_commercial_secret(
        self, qdrant_client: QdrantClient, test_chunks: list[DocumentChunk]
    ) -> None:
        index_chunks(qdrant_client, test_chunks, "test_collection")
        retriever = DenseRetriever(qdrant_client, "test_collection")
        results = retriever.search("коммерческая тайна", top_k=3)
        assert len(results) >= 1
        assert results[0].chunk.document_title == "98-ФЗ"

    def test_search_preserves_provenance(
        self, qdrant_client: QdrantClient, test_chunks: list[DocumentChunk]
    ) -> None:
        index_chunks(qdrant_client, test_chunks, "test_collection")
        retriever = DenseRetriever(qdrant_client, "test_collection")
        results = retriever.search("персональные данные", top_k=3)
        chunk = results[0].chunk
        assert chunk.chunk_id == "550e8400-e29b-41d4-a716-446655440001"
        assert chunk.source_path == "laws/152fz.md"
        assert chunk.heading == "Персональные данные"

    def test_loads_from_real_corpus(self, qdrant_client: QdrantClient) -> None:
        """Test indexing the actual legal corpus."""
        project_root = Path(__file__).parent.parent
        laws_dir = project_root / "data" / "raw" / "laws"
        if laws_dir.is_dir():
            chunks = load_corpus(laws_dir)
            assert len(chunks) > 0
            index_chunks(qdrant_client, chunks, "real_corpus")
            retriever = DenseRetriever(qdrant_client, "real_corpus")
            results = retriever.search("требования к защите персональных данных", top_k=5)
            assert len(results) > 0
            assert any("152" in r.chunk.document_title for r in results)
