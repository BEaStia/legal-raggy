"""Tests for hybrid citation attachment."""

from pathlib import Path

import pytest

from app.models import (
    ArchitectureProfile,
    ComplianceAssessment,
    Confidence,
    DataCategory,
    RegulatoryTrigger,
)
from app.services.citations import attach_citation


class TestHybridCitations:
    """Citation service tests with hybrid retrieval fallback."""

    @pytest.fixture
    def laws_dir(self) -> Path:
        return Path(__file__).parent.parent / "data" / "raw" / "laws"

    def _assessment_with_trigger(
        self, trigger_id: str, basis: list[str]
    ) -> ComplianceAssessment:
        profile = ArchitectureProfile(
            source_description="test",
            data_categories=[DataCategory.personal_data],
        )
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="test",
            regulatory_triggers=[],
            citations=[],
            disclaimer="test",
        )
        assessment.regulatory_triggers.append(
            RegulatoryTrigger(
                id=trigger_id,
                title="test",
                description="test",
                basis=basis,
                confidence=Confidence.high,
            )
        )
        return assessment

    def test_pd_trigger_cites_152fz(self, laws_dir: Path) -> None:
        assessment = self._assessment_with_trigger(
            "personal_data_processing", ["152-ФЗ"]
        )
        result = attach_citation(assessment, laws_dir)
        assert len(result.citations) >= 1
        assert any("152" in c.document_title for c in result.citations)

    def test_signature_trigger_cites_63fz(self, laws_dir: Path) -> None:
        assessment = self._assessment_with_trigger(
            "electronic_signature_regulation", ["63-ФЗ"]
        )
        result = attach_citation(assessment, laws_dir)
        assert len(result.citations) >= 1
        assert any("63" in c.document_title for c in result.citations)

    def test_commercial_secret_cites_98fz(self, laws_dir: Path) -> None:
        assessment = self._assessment_with_trigger(
            "commercial_secret_possible", ["98-ФЗ"]
        )
        result = attach_citation(assessment, laws_dir)
        assert len(result.citations) >= 1
        assert any("98" in c.document_title for c in result.citations)

    def test_no_triggers_no_citations(self, laws_dir: Path) -> None:
        profile = ArchitectureProfile(source_description="test")
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="test",
            regulatory_triggers=[],
            citations=[],
            disclaimer="test",
        )
        result = attach_citation(assessment, laws_dir)
        assert result.citations == []

    def test_missing_corpus_no_citations(self) -> None:
        assessment = self._assessment_with_trigger(
            "personal_data_processing", ["152-ФЗ"]
        )
        result = attach_citation(assessment, Path("/nonexistent"))
        assert result.citations == []

    def test_citations_have_provenance(self, laws_dir: Path) -> None:
        assessment = self._assessment_with_trigger(
            "personal_data_processing", ["152-ФЗ"]
        )
        result = attach_citation(assessment, laws_dir)
        for citation in result.citations:
            assert citation.chunk_id is not None
            assert citation.source is not None
            assert citation.quote is not None

    def test_force_keyword_fallback(self, laws_dir: Path) -> None:
        """use_hybrid=False should still work with keyword-only."""
        assessment = self._assessment_with_trigger(
            "personal_data_processing", ["152-ФЗ"]
        )
        result = attach_citation(assessment, laws_dir, use_hybrid=False)
        assert len(result.citations) >= 1
        assert any("152" in c.document_title for c in result.citations)

    def test_multiple_triggers_multiple_citations(self, laws_dir: Path) -> None:
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
                    title="PD",
                    description="test",
                    basis=["152-ФЗ"],
                    confidence=Confidence.high,
                ),
                RegulatoryTrigger(
                    id="electronic_signature_regulation",
                    title="ES",
                    description="test",
                    basis=["63-ФЗ"],
                    confidence=Confidence.medium,
                ),
            ],
            citations=[],
            disclaimer="test",
        )
        result = attach_citation(assessment, laws_dir)
        assert len(result.citations) >= 2
        titles = {c.document_title for c in result.citations}
        assert any("152" in t for t in titles)
        assert any("63" in t for t in titles)
