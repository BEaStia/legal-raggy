import json

import pytest
from pydantic import ValidationError

from app.models import (
    AdminAccess,
    ArchitectureProfile,
    ArchitectureType,
    ClarificationQuestion,
    ComplianceAssessment,
    Confidence,
    DataCategory,
    Exposure,
    Integration,
    IntegrationType,
    LegalCitation,
    RecommendedControl,
    RedFlag,
    RegulatoryTrigger,
    Severity,
    StorageLocation,
)


@pytest.mark.parametrize(
    "model, field",
    [
        (ArchitectureProfile, "architecture_type"),
        (ArchitectureProfile, "exposure"),
        (ArchitectureProfile, "data_categories"),
        (ArchitectureProfile, "storage_location"),
        (Integration, "type"),
        (Integration, "location"),
        (RegulatoryTrigger, "confidence"),
        (RedFlag, "severity"),
        (RecommendedControl, "priority"),
    ],
)
def test_models_reject_unknown_enum_values(model: type, field: str) -> None:
    valid_fields: dict[str, object]
    if model is ArchitectureProfile:
        valid_fields = {"source_description": "B2B SaaS"}
    elif model is RegulatoryTrigger:
        valid_fields = {"id": "trigger", "title": "Trigger", "description": "Description"}
    elif model is RedFlag:
        valid_fields = {"id": "flag", "title": "Flag", "description": "Description"}
    elif model is RecommendedControl:
        valid_fields = {"id": "control", "title": "Control", "description": "Description"}
    else:
        valid_fields = {}

    invalid_value: object = ["invented_value"] if field == "data_categories" else "invented_value"

    with pytest.raises(ValidationError):
        model(**valid_fields, **{field: invalid_value})


def test_architecture_profile_defaults_are_not_shared() -> None:
    first = ArchitectureProfile(source_description="First")
    second = ArchitectureProfile(source_description="Second")

    first.users.append("administrator")
    first.admin_access.exists = True

    assert second.users == []
    assert second.admin_access.exists is None


def test_legal_conclusions_are_required_instead_of_defaulted() -> None:
    profile = ArchitectureProfile(source_description="B2B SaaS")

    with pytest.raises(ValidationError) as error:
        ComplianceAssessment(architecture_profile=profile)

    missing_fields = {item["loc"][0] for item in error.value.errors()}
    assert missing_fields == {"summary", "disclaimer"}

    with pytest.raises(ValidationError):
        ArchitectureProfile()


def test_section_17_example_round_trips_through_json() -> None:
    assessment = ComplianceAssessment(
        architecture_profile=ArchitectureProfile(
            source_description=(
                "У нас B2B SaaS для клиентов. Пользователи регистрируются по email и "
                "телефону. Есть личный кабинет и админка."
            ),
            architecture_type=ArchitectureType.b2b_saas,
            exposure=Exposure.public_internet,
            users=["client"],
            data_categories=[
                DataCategory.personal_data,
                DataCategory.telemetry_logs,
                DataCategory.payment_data,
            ],
            raw_data_items=["email", "phone"],
            storage_location=StorageLocation.russia,
            integrations=[
                Integration(
                    name="Sentry",
                    type=IntegrationType.observability,
                    sends_personal_data=True,
                    location=StorageLocation.foreign,
                ),
                Integration(name="Payment provider", type=IntegrationType.payment_provider),
            ],
            admin_access=AdminAccess(exists=True, exposed_to_internet=True, mfa_enabled=False),
            has_payments=True,
            has_logs_or_observability=True,
        ),
        summary="Обнаружены признаки обработки персональных данных.",
        regulatory_triggers=[
            RegulatoryTrigger(
                id="personal_data_processing",
                title="Обработка персональных данных",
                description="Предварительно обнаружены персональные данные.",
                basis=["152-ФЗ"],
                confidence=Confidence.high,
            )
        ],
        red_flags=[
            RedFlag(
                id="internet_exposed_admin_panel",
                title="Админ-панель доступна из интернета",
                description="Требуется проверить ограничения доступа.",
                severity=Severity.high,
            )
        ],
        recommended_controls=[
            RecommendedControl(
                id="enable_mfa",
                title="Включить MFA",
                description="Добавить второй фактор для административного доступа.",
                priority=Severity.high,
                related_triggers=["personal_data_processing"],
            )
        ],
        clarification_questions=[
            ClarificationQuestion(
                id="sentry_location",
                question="Где обрабатываются данные Sentry?",
                reason="Нужно уточнить трансграничную передачу.",
                related_triggers=["personal_data_processing"],
            )
        ],
        citations=[
            LegalCitation(document_title="152-ФЗ", article="5", source="official-source")
        ],
        disclaimer="Предварительная оценка; требуется проверка юристом.",
    )

    payload = json.loads(assessment.model_dump_json())
    restored = ComplianceAssessment.model_validate_json(json.dumps(payload))

    assert restored == assessment
    assert payload["architecture_profile"]["architecture_type"] == "b2b_saas"
    assert payload["architecture_profile"]["data_categories"] == [
        "personal_data",
        "telemetry_logs",
        "payment_data",
    ]
    assert payload["needs_human_security_review"] is True
    assert payload["needs_human_legal_review"] is True
