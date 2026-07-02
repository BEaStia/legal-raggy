"""Tests for the Markdown assessment renderer."""

from app.generation.renderer import render_assessment_markdown
from app.models import (
    AdminAccess,
    ArchitectureProfile,
    ArchitectureType,
    ClarificationQuestion,
    ComplianceAssessment,
    Confidence,
    DataCategory,
    Exposure,
    LegalCitation,
    RecommendedControl,
    RedFlag,
    RegulatoryTrigger,
    Severity,
    StorageLocation,
)


def _minimal_assessment() -> ComplianceAssessment:
    return ComplianceAssessment(
        architecture_profile=ArchitectureProfile(
            source_description="Внутренний сервис без данных.",
        ),
        summary="Значимых регуляторных триггеров не обнаружено.",
        disclaimer="Предварительная оценка; требуется проверка специалистом.",
    )


def _full_assessment() -> ComplianceAssessment:
    return ComplianceAssessment(
        architecture_profile=ArchitectureProfile(
            source_description="B2B SaaS с email и телефоном.",
            architecture_type=ArchitectureType.b2b_saas,
            exposure=Exposure.public_internet,
            data_categories=[DataCategory.personal_data],
            raw_data_items=["email", "phone"],
            storage_location=StorageLocation.russia,
            admin_access=AdminAccess(
                exists=True,
                exposed_to_internet=True,
                mfa_enabled=False,
            ),
        ),
        summary="Обнаружены признаки обработки персональных данных.",
        regulatory_triggers=[
            RegulatoryTrigger(
                id="personal_data_processing",
                title="Обработка персональных данных",
                description="Обнаружены ПДн.",
                basis=["152-ФЗ"],
                confidence=Confidence.high,
            )
        ],
        red_flags=[
            RedFlag(
                id="internet_exposed_admin_panel",
                title="Админка из интернета",
                description="Админ-панель доступна из публичной сети.",
                severity=Severity.high,
            )
        ],
        recommended_controls=[
            RecommendedControl(
                id="enable_mfa",
                title="Включить MFA",
                description="Добавить второй фактор.",
                priority=Severity.high,
                related_triggers=["personal_data_processing"],
            )
        ],
        clarification_questions=[
            ClarificationQuestion(
                id="pd_storage",
                question="Где хранятся ПДн?",
                reason="Необходимо определить юрисдикцию.",
                related_triggers=["personal_data_processing"],
            )
        ],
        citations=[
            LegalCitation(
                document_title="152-ФЗ",
                document_type="federal_law",
                article="5",
            )
        ],
        disclaimer="Предварительная оценка; требуется проверка специалистом.",
    )


def test_minimal_assessment_has_all_sections() -> None:
    markdown = render_assessment_markdown(_minimal_assessment())

    assert "# Preliminary IT Compliance Assessment" in markdown
    assert "## Summary" in markdown
    assert "## Detected architecture profile" in markdown
    assert "## Regulatory triggers" in markdown
    assert "## Red flags" in markdown
    assert "## Recommended controls" in markdown
    assert "## Clarification questions" in markdown
    assert "## Sources / citations" in markdown
    assert "## Disclaimer" in markdown


def test_minimal_assessment_shows_empty_lists() -> None:
    markdown = render_assessment_markdown(_minimal_assessment())

    assert "No regulatory triggers detected." in markdown
    assert "No red flags detected." in markdown
    assert "No recommended controls." in markdown
    assert "No clarification questions." in markdown


def test_full_assessment_includes_trigger_details() -> None:
    markdown = render_assessment_markdown(_full_assessment())

    assert "personal_data_processing" in markdown
    assert "Обработка персональных данных" in markdown
    assert "152-ФЗ" in markdown
    assert "high" in markdown


def test_full_assessment_includes_red_flag_severity() -> None:
    markdown = render_assessment_markdown(_full_assessment())

    assert "internet_exposed_admin_panel" in markdown
    assert "Админка из интернета" in markdown
    assert "high" in markdown


def test_full_assessment_includes_control_with_related_triggers() -> None:
    markdown = render_assessment_markdown(_full_assessment())

    assert "enable_mfa" in markdown
    assert "Включить MFA" in markdown
    assert "personal_data_processing" in markdown


def test_full_assessment_includes_question() -> None:
    markdown = render_assessment_markdown(_full_assessment())

    assert "Где хранятся ПДн?" in markdown
    assert "Необходимо определить юрисдикцию." in markdown


def test_full_assessment_includes_citation() -> None:
    markdown = render_assessment_markdown(_full_assessment())

    assert "152-ФЗ" in markdown
    assert "federal_law" in markdown
    assert "Article: 5" in markdown


def test_disclaimer_is_always_present() -> None:
    assessment = _minimal_assessment()
    markdown = render_assessment_markdown(assessment)

    assert assessment.disclaimer in markdown


def test_architecture_profile_shows_key_fields() -> None:
    markdown = render_assessment_markdown(_full_assessment())

    assert "b2b_saas" in markdown
    assert "public_internet" in markdown
    assert "personal_data" in markdown
    assert "email" in markdown
    assert "phone" in markdown
    assert "russia" in markdown


def test_human_review_flags_shown() -> None:
    markdown = render_assessment_markdown(_full_assessment())

    assert "Human security review required" in markdown
    assert "Human legal review required" in markdown


def test_empty_citations_shows_message() -> None:
    markdown = render_assessment_markdown(_minimal_assessment())

    assert "No citations available." in markdown


def test_renderer_is_deterministic() -> None:
    assessment = _full_assessment()

    first = render_assessment_markdown(assessment)
    second = render_assessment_markdown(assessment)

    assert first == second
