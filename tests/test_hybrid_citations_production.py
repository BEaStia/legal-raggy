"""Tests for hybrid citations in production pipeline.

Compares hybrid vs keyword retrieval quality with real laws.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from qdrant_client import QdrantClient

from app.agents.graph import run_workflow
from app.ingestion.chunking import load_corpus
from app.models import (
    ArchitectureProfile,
    ComplianceAssessment,
    Confidence,
    DataCategory,
    RegulatoryTrigger,
)
from app.retrieval.qdrant_store import index_chunks
from app.services.analyze import run_analysis
from app.services.citations import attach_citation


@pytest.fixture
def laws_dir() -> Path:
    return Path(__file__).parent.parent / "data" / "raw" / "laws"


@pytest.fixture
def qdrant_client() -> QdrantClient:
    return QdrantClient(":memory:")


@pytest.fixture
def indexed_qdrant(qdrant_client: QdrantClient, laws_dir: Path) -> QdrantClient:
    chunks = load_corpus(laws_dir)
    if chunks:
        index_chunks(qdrant_client, chunks, "test_hybrid_prod")
    return qdrant_client


class TestHybridVsKeyword:
    """Compare hybrid vs keyword retrieval quality."""

    def test_hybrid_returns_more_citations(
        self,
        qdrant_client: QdrantClient,
        indexed_qdrant: QdrantClient,
        laws_dir: Path,
    ) -> None:
        """Hybrid should return >= citations than keyword-only."""
        profile = ArchitectureProfile(
            source_description="B2B SaaS с email и телефоном",
            data_categories=[DataCategory.personal_data],
        )
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="test",
            regulatory_triggers=[
                RegulatoryTrigger(
                    id="personal_data_processing",
                    title="test",
                    description="test",
                    basis=["152-ФЗ"],
                    confidence=Confidence.high,
                )
            ],
            citations=[],
            disclaimer="test",
        )

        # Keyword-only
        kw_result = attach_citation(
            assessment, laws_dir=laws_dir, use_hybrid=False
        )

        # Hybrid (with mocked Qdrant)
        with patch(
            "app.services.citations._try_create_qdrant_client",
            return_value=indexed_qdrant,
        ):
            hybrid_result = attach_citation(
                ComplianceAssessment(
                    architecture_profile=profile,
                    summary="test",
                    regulatory_triggers=assessment.regulatory_triggers,
                    citations=[],
                    disclaimer="test",
                ),
                laws_dir=laws_dir,
                use_hybrid=True,
            )

        assert len(hybrid_result.citations) >= len(kw_result.citations)

    def test_hybrid_fallback_to_keyword(
        self, laws_dir: Path
    ) -> None:
        """When Qdrant unavailable, hybrid falls back to keyword."""
        profile = ArchitectureProfile(
            source_description="test",
            data_categories=[DataCategory.personal_data],
        )
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="test",
            regulatory_triggers=[
                RegulatoryTrigger(
                    id="personal_data_processing",
                    title="test",
                    description="test",
                    basis=["152-ФЗ"],
                    confidence=Confidence.high,
                )
            ],
            citations=[],
            disclaimer="test",
        )

        with patch(
            "app.services.citations._try_create_qdrant_client",
            return_value=None,
        ):
            result = attach_citation(
                assessment, laws_dir=laws_dir, use_hybrid=True
            )

        # Should still have citations (from keyword fallback)
        assert len(result.citations) >= 1

    def test_run_analysis_uses_hybrid_when_qdrant_available(
        self,
        indexed_qdrant: QdrantClient,
        laws_dir: Path,
    ) -> None:
        """run_analysis should use hybrid when Qdrant is available."""
        with patch(
            "app.services.citations._try_create_qdrant_client",
            return_value=indexed_qdrant,
        ):
            result = run_analysis(
                "B2B SaaS, регистрация по email",
                laws_dirs=[laws_dir],
            )

        assert len(result.citations) >= 1
        assert any("152" in c.document_title for c in result.citations)


class TestProductionPipeline:
    """Integration tests for full production pipeline."""

    def test_full_pipeline_with_hybrid(
        self,
        indexed_qdrant: QdrantClient,
        laws_dir: Path,
    ) -> None:
        """Full pipeline should produce citations with hybrid retrieval."""
        with patch(
            "app.services.citations._try_create_qdrant_client",
            return_value=indexed_qdrant,
        ):
            result = run_analysis(
                (
                    "У нас B2B SaaS. Пользователи регистрируются "
                    "по email и телефону. База в РФ."
                ),
                laws_dirs=[laws_dir],
            )

        assert result.architecture_profile.architecture_type is not None
        assert len(result.regulatory_triggers) >= 1
        assert len(result.citations) >= 1

    def test_workflow_with_hybrid(
        self,
        indexed_qdrant: QdrantClient,
        laws_dir: Path,
    ) -> None:
        """LangGraph workflow should work with hybrid citations."""
        with patch(
            "app.services.citations._try_create_qdrant_client",
            return_value=indexed_qdrant,
        ):
            result = run_workflow(
                "B2B SaaS с email регистрацией",
                laws_dir=laws_dir,
            )

        assert result["final_assessment"] is not None
        assert len(result["citations"]) >= 1

    def test_citations_have_full_provenance(
        self,
        indexed_qdrant: QdrantClient,
        laws_dir: Path,
    ) -> None:
        """Citations should have complete provenance info."""
        with patch(
            "app.services.citations._try_create_qdrant_client",
            return_value=indexed_qdrant,
        ):
            result = run_analysis(
                "Сервис с электронной подписью УКЭП",
                laws_dirs=[laws_dir],
            )

        for citation in result.citations:
            assert citation.document_title is not None
            assert citation.chunk_id is not None
            assert citation.quote is not None
            assert citation.source is not None
