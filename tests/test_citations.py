"""Tests for citation attachment to compliance assessments."""

from pathlib import Path

import pytest

from app.models import (
    ArchitectureProfile,
    ComplianceAssessment,
    Confidence,
    DataCategory,
    RegulatoryTrigger,
)
from app.services.analyze import run_analysis
from app.services.citations import attach_citation


class TestAttachCitations:
    """Citation service tests with real corpus."""

    @pytest.fixture
    def project_root(self) -> Path:
        return Path(__file__).parent.parent

    @pytest.fixture
    def laws_dir(self, project_root: Path) -> Path:
        return project_root / "data" / "raw" / "laws"

    def test_personal_data_trigger_cites_152fz(self, laws_dir: Path) -> None:
        """personal_data_processing trigger must cite 152-ФЗ."""
        profile = ArchitectureProfile(
            source_description="Собираем email и телефон пользователей",
            data_categories=[DataCategory.personal_data],
        )
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="Обнаружены ПДн.",
            regulatory_triggers=[],
            citations=[],
            disclaimer="test",
        )
        # Manually add trigger to test citation mapping
        assessment.regulatory_triggers.append(
            RegulatoryTrigger(
                id="personal_data_processing",
                title="Обработка ПДн",
                description="test",
                basis=["152-ФЗ"],
                confidence=Confidence.high,
            )
        )

        result = attach_citation(assessment, laws_dir)
        assert len(result.citations) >= 1
        assert any("152" in c.document_title for c in result.citations)

    def test_electronic_signature_trigger_cites_63fz(self, laws_dir: Path) -> None:
        """electronic_signature_regulation trigger must cite 63-ФЗ."""
        profile = ArchitectureProfile(
            source_description="Подписываем документы электронной подписью",
            has_electronic_signature=True,
        )
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="Обнаружена ЭП.",
            regulatory_triggers=[],
            citations=[],
            disclaimer="test",
        )
        assessment.regulatory_triggers.append(
            RegulatoryTrigger(
                id="electronic_signature_regulation",
                title="Регулирование ЭП",
                description="test",
                basis=["63-ФЗ"],
                confidence=Confidence.medium,
            )
        )

        result = attach_citation(assessment, laws_dir)
        assert len(result.citations) >= 1
        assert any("63" in c.document_title for c in result.citations)

    def test_commercial_secret_trigger_cites_98fz(self, laws_dir: Path) -> None:
        """commercial_secret_possible trigger must cite 98-ФЗ."""
        profile = ArchitectureProfile(
            source_description="Храним source code и internal analytics",
        )
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="Обнаружена коммерческая тайна.",
            regulatory_triggers=[],
            citations=[],
            disclaimer="test",
        )
        assessment.regulatory_triggers.append(
            RegulatoryTrigger(
                id="commercial_secret_possible",
                title="Коммерческая тайна",
                description="test",
                basis=["98-ФЗ"],
                confidence=Confidence.medium,
            )
        )

        result = attach_citation(assessment, laws_dir)
        assert len(result.citations) >= 1
        assert any("98" in c.document_title for c in result.citations)

    def test_no_triggers_produces_no_citations(self, laws_dir: Path) -> None:
        """Assessment with no triggers should have no citations."""
        profile = ArchitectureProfile(
            source_description="Внутренний сервис без данных",
        )
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="Ничего не найдено.",
            regulatory_triggers=[],
            citations=[],
            disclaimer="test",
        )

        result = attach_citation(assessment, laws_dir)
        assert result.citations == []

    def test_citations_have_provenance(self, laws_dir: Path) -> None:
        """Each citation must have chunk_id and source_path."""
        profile = ArchitectureProfile(
            source_description="Собираем email пользователей",
            data_categories=[DataCategory.personal_data],
        )
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="ПДн обнаружены.",
            regulatory_triggers=[],
            citations=[],
            disclaimer="test",
        )
        assessment.regulatory_triggers.append(
            RegulatoryTrigger(
                id="personal_data_processing",
                title="Обработка ПДн",
                description="test",
                basis=["152-ФЗ"],
                confidence=Confidence.high,
            )
        )

        result = attach_citation(assessment, laws_dir)
        for citation in result.citations:
            assert citation.chunk_id is not None
            assert citation.source is not None

    def test_missing_corpus_returns_empty_citations(self) -> None:
        """Non-existent laws directory should not crash, returns no citations."""
        profile = ArchitectureProfile(
            source_description="Собираем email",
            data_categories=[DataCategory.personal_data],
        )
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary="ПДн.",
            regulatory_triggers=[],
            citations=[],
            disclaimer="test",
        )
        assessment.regulatory_triggers.append(
            RegulatoryTrigger(
                id="personal_data_processing",
                title="test",
                description="test",
                basis=["152-ФЗ"],
                confidence=Confidence.high,
            )
        )

        result = attach_citation(assessment, Path("/nonexistent/path"))
        assert result.citations == []


class TestRunAnalysisWithCitations:
    """Integration tests: full pipeline with citations."""

    @pytest.fixture
    def laws_dir(self) -> Path:
        return Path(__file__).parent.parent / "data" / "raw" / "laws"

    def test_full_pipeline_includes_citations_for_pd(self, laws_dir: Path) -> None:
        """Full analysis of PD description must include 152-ФЗ citations."""
        description = (
            "У нас B2B SaaS. Пользователи регистрируются по email и телефону. "
            "База в РФ. Логи уходят в Sentry."
        )
        assessment = run_analysis(description, laws_dirs=[laws_dir])
        assert len(assessment.citations) >= 1
        assert any("152" in c.document_title for c in assessment.citations)

    def test_full_pipeline_includes_citations_for_signature(self, laws_dir: Path) -> None:
        """Analysis with e-signature must include 63-ФЗ citations."""
        description = (
            "Сервис подписывает документы электронной подписью. "
            "Используем УКЭП для юридически значимых действий."
        )
        assessment = run_analysis(description, laws_dirs=[laws_dir])
        assert len(assessment.citations) >= 1
        assert any("63" in c.document_title for c in assessment.citations)

    def test_full_pipeline_includes_citations_for_commercial_secret(self, laws_dir: Path) -> None:
        """Analysis with commercial secret markers must include 98-ФЗ citations."""
        description = (
            "Храним source code, customer database и financial reports. "
            "Это коммерческая тайна компании."
        )
        assessment = run_analysis(description, laws_dirs=[laws_dir])
        assert len(assessment.citations) >= 1
        assert any("98" in c.document_title for c in assessment.citations)

    def test_citations_preserve_assessment_structure(self, laws_dir: Path) -> None:
        """Adding citations must not break other assessment fields."""
        description = (
            "У нас B2B SaaS. Пользователи регистрируются по email и телефону. "
            "Админка доступна из интернета, MFA нет. База в РФ."
        )
        assessment = run_analysis(description, laws_dirs=[laws_dir])
        assert assessment.architecture_profile.architecture_type is not None
        assert assessment.summary != ""
        assert assessment.disclaimer != ""
        assert assessment.needs_human_security_review is True
        assert assessment.needs_human_legal_review is True
