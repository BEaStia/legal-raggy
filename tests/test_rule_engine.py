"""Tests for the deterministic compliance rule engine."""

from app.models import (
    AdminAccess,
    ArchitectureProfile,
    ArchitectureType,
    DataCategory,
    Exposure,
    Integration,
    IntegrationType,
    StorageLocation,
)
from app.rules.engine import analyze_profile


def _golden_profile() -> ArchitectureProfile:
    """Section 15.2 golden profile."""
    return ArchitectureProfile(
        source_description=(
            "У нас B2B SaaS, пользователи регистрируются по email и телефону. "
            "Админка доступна из интернета. MFA нет. Логи уходят в Sentry."
        ),
        architecture_type=ArchitectureType.b2b_saas,
        exposure=Exposure.public_internet,
        users=["users"],
        data_categories=[DataCategory.personal_data, DataCategory.telemetry_logs],
        raw_data_items=["email", "phone"],
        storage_location=StorageLocation.russia,
        integrations=[
            Integration(
                name="Sentry",
                type=IntegrationType.observability,
                sends_personal_data=True,
            )
        ],
        admin_access=AdminAccess(
            exists=True,
            exposed_to_internet=True,
            mfa_enabled=False,
        ),
        has_logs_or_observability=True,
    )


def test_golden_profile_produces_required_triggers() -> None:
    assessment = analyze_profile(_golden_profile())

    trigger_ids = {t.id for t in assessment.regulatory_triggers}
    assert "personal_data_processing" in trigger_ids
    assert "possible_ispdn" in trigger_ids


def test_golden_profile_produces_required_red_flags() -> None:
    assessment = analyze_profile(_golden_profile())

    flag_ids = {f.id for f in assessment.red_flags}
    assert "possible_personal_data_in_logs" in flag_ids
    assert "internet_exposed_admin_panel" in flag_ids
    assert "admin_mfa_missing_or_unknown" in flag_ids


def test_golden_profile_produces_required_controls() -> None:
    assessment = analyze_profile(_golden_profile())

    control_ids = {c.id for c in assessment.recommended_controls}
    assert "enable_mfa" in control_ids
    assert "mask_personal_data_in_logs" in control_ids


def test_golden_profile_has_summary_and_disclaimer() -> None:
    assessment = analyze_profile(_golden_profile())

    assert assessment.summary
    assert assessment.disclaimer


def test_golden_profile_preserves_architecture_profile() -> None:
    profile = _golden_profile()
    assessment = analyze_profile(profile)

    assert assessment.architecture_profile is profile


def test_no_personal_data_produces_no_pd_triggers() -> None:
    profile = ArchitectureProfile(
        source_description="Internal service without user data.",
        architecture_type=ArchitectureType.internal_service,
        exposure=Exposure.internal_network,
    )
    assessment = analyze_profile(profile)

    trigger_ids = {t.id for t in assessment.regulatory_triggers}
    assert "personal_data_processing" not in trigger_ids
    assert "possible_ispdn" not in trigger_ids


def test_admin_not_exposed_has_no_admin_red_flag() -> None:
    profile = ArchitectureProfile(
        source_description="Internal service. Админка есть, но только через VPN.",
        architecture_type=ArchitectureType.internal_service,
        exposure=Exposure.vpn,
        admin_access=AdminAccess(
            exists=True,
            exposed_to_internet=False,
            mfa_enabled=True,
        ),
    )
    assessment = analyze_profile(profile)

    flag_ids = {f.id for f in assessment.red_flags}
    assert "internet_exposed_admin_panel" not in flag_ids
    assert "admin_mfa_missing_or_unknown" not in flag_ids


def test_payments_trigger() -> None:
    profile = ArchitectureProfile(
        source_description="B2B SaaS с платежами.",
        architecture_type=ArchitectureType.b2b_saas,
        has_payments=True,
    )
    assessment = analyze_profile(profile)

    trigger_ids = {t.id for t in assessment.regulatory_triggers}
    assert "payment_regulation_possible" in trigger_ids


def test_electronic_signature_trigger() -> None:
    profile = ArchitectureProfile(
        source_description="Сервис с электронной подписью.",
        has_electronic_signature=True,
    )
    assessment = analyze_profile(profile)

    trigger_ids = {t.id for t in assessment.regulatory_triggers}
    assert "electronic_signature_regulation" in trigger_ids


def test_kii_trigger() -> None:
    profile = ArchitectureProfile(
        source_description="Система для субъекта КИИ.",
        serves_kii_subject=True,
    )
    assessment = analyze_profile(profile)

    trigger_ids = {t.id for t in assessment.regulatory_triggers}
    assert "kii_relevance_possible" in trigger_ids
    assert assessment.needs_human_security_review is True


def test_external_integration_with_personal_data_flags() -> None:
    profile = ArchitectureProfile(
        source_description="B2B SaaS. Данные отправляются в CRM.",
        architecture_type=ArchitectureType.b2b_saas,
        data_categories=[DataCategory.personal_data],
        integrations=[
            Integration(
                name="CRM",
                type=IntegrationType.crm,
                sends_personal_data=True,
            )
        ],
    )
    assessment = analyze_profile(profile)

    flag_ids = {f.id for f in assessment.red_flags}
    assert "external_processor_or_transfer_unknown" in flag_ids


def test_external_integration_unknown_sends_personal_data_flags() -> None:
    profile = ArchitectureProfile(
        source_description="B2B SaaS. Интеграция с аналитикой.",
        architecture_type=ArchitectureType.b2b_saas,
        data_categories=[DataCategory.personal_data],
        integrations=[
            Integration(
                name="Google Analytics",
                type=IntegrationType.analytics,
                sends_personal_data=None,
            )
        ],
    )
    assessment = analyze_profile(profile)

    flag_ids = {f.id for f in assessment.red_flags}
    assert "external_processor_or_transfer_unknown" in flag_ids


def test_external_integration_without_personal_data_no_flag() -> None:
    profile = ArchitectureProfile(
        source_description="B2B SaaS. CRM без персональных данных.",
        architecture_type=ArchitectureType.b2b_saas,
        integrations=[
            Integration(
                name="CRM",
                type=IntegrationType.crm,
                sends_personal_data=False,
            )
        ],
    )
    assessment = analyze_profile(profile)

    flag_ids = {f.id for f in assessment.red_flags}
    assert "external_processor_or_transfer_unknown" not in flag_ids


def test_clarification_questions_for_personal_data() -> None:
    assessment = analyze_profile(_golden_profile())

    assert len(assessment.clarification_questions) > 0
    for q in assessment.clarification_questions:
        assert q.question
        assert q.reason


def test_controls_have_related_triggers() -> None:
    assessment = analyze_profile(_golden_profile())

    for control in assessment.recommended_controls:
        assert len(control.related_triggers) > 0


def test_human_review_flags_default_true() -> None:
    profile = ArchitectureProfile(
        source_description="Minimal service.",
    )
    assessment = analyze_profile(profile)

    assert assessment.needs_human_security_review is True
    assert assessment.needs_human_legal_review is True
