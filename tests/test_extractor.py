import pytest

from app.models import ArchitectureType, DataCategory, Exposure, IntegrationType, StorageLocation
from app.rules.architecture_patterns import extract_architecture_profile

GOLDEN_DESCRIPTION = (
    "У нас B2B SaaS, пользователи регистрируются по email и телефону. "
    "Админка доступна из интернета. MFA нет. Логи уходят в Sentry."
)


def test_extracts_section_15_2_golden_profile() -> None:
    profile = extract_architecture_profile(GOLDEN_DESCRIPTION)

    assert profile.source_description == GOLDEN_DESCRIPTION
    assert profile.architecture_type is ArchitectureType.b2b_saas
    assert profile.exposure is Exposure.public_internet
    assert DataCategory.personal_data in profile.data_categories
    assert profile.raw_data_items == ["email", "phone"]
    assert profile.has_logs_or_observability is True
    assert profile.admin_access.exists is True
    assert profile.admin_access.exposed_to_internet is True
    assert profile.admin_access.mfa_enabled is False
    assert [(item.name, item.type) for item in profile.integrations] == [
        ("Sentry", IntegrationType.observability)
    ]


def test_extracts_basic_english_keywords() -> None:
    profile = extract_architecture_profile(
        "B2B SaaS users register with e-mail and phone. "
        "Admin panel is available on public internet. No MFA. Logs go to Sentry."
    )

    assert profile.architecture_type is ArchitectureType.b2b_saas
    assert profile.exposure is Exposure.public_internet
    assert profile.raw_data_items == ["email", "phone"]
    assert DataCategory.personal_data in profile.data_categories
    assert profile.has_logs_or_observability is True
    assert profile.admin_access.exists is True
    assert profile.admin_access.exposed_to_internet is True
    assert profile.admin_access.mfa_enabled is False


def test_extracts_section_17_storage_payments_and_log_transfer() -> None:
    description = (
        "У нас B2B SaaS для клиентов. Пользователи регистрируются по email и телефону. "
        "Есть личный кабинет и админка. Админка доступна из интернета, MFA пока нет. "
        "База данных находится в российском облаке. Логи ошибок отправляются в Sentry, "
        "туда может попадать email пользователя. Есть платежный провайдер для оплаты подписки."
    )

    profile = extract_architecture_profile(description)

    assert profile.storage_location is StorageLocation.russia
    assert profile.has_payments is True
    assert profile.has_logs_or_observability is True
    assert profile.data_categories == [
        DataCategory.personal_data,
        DataCategory.payment_data,
        DataCategory.telemetry_logs,
    ]
    assert [(item.name, item.type) for item in profile.integrations] == [
        ("Sentry", IntegrationType.observability),
        ("Payment provider", IntegrationType.payment_provider),
    ]
    assert profile.integrations[0].sends_personal_data is True


@pytest.mark.parametrize(
    ("description", "architecture_type", "exposure"),
    [
        (
            "ПУБЛИЧНЫЙ САЙТ доступен в ИНТЕРНЕТЕ",
            ArchitectureType.public_website,
            Exposure.public_internet,
        ),
        (
            "Internal service доступен только через VPN",
            ArchitectureType.internal_service,
            Exposure.vpn,
        ),
        ("Сервис работает в закрытом контуре", ArchitectureType.unknown, Exposure.closed_contour),
    ],
)
def test_normalizes_case_and_detects_basic_architecture(
    description: str,
    architecture_type: ArchitectureType,
    exposure: Exposure,
) -> None:
    profile = extract_architecture_profile(description)

    assert profile.architecture_type is architecture_type
    assert profile.exposure is exposure


def test_uses_word_boundaries_and_respects_explicit_admin_negation() -> None:
    profile = extract_architecture_profile(
        "Описание API без пользовательских данных. Админки нет. MFA не используется."
    )

    assert "ip" not in profile.raw_data_items
    assert DataCategory.personal_data not in profile.data_categories
    assert profile.admin_access.exists is False
    assert profile.admin_access.exposed_to_internet is None
    assert profile.admin_access.mfa_enabled is None


@pytest.mark.parametrize("description", ["Логирование отключено", "Service has no logs"])
def test_log_negation_does_not_create_telemetry(description: str) -> None:
    profile = extract_architecture_profile(description)

    assert profile.has_logs_or_observability is False
    assert DataCategory.telemetry_logs not in profile.data_categories


def test_english_public_exposure_negation_is_respected() -> None:
    profile = extract_architecture_profile(
        "Admin panel is not available on public internet. No MFA."
    )

    assert profile.exposure is Exposure.unknown
    assert profile.admin_access.exists is True
    assert profile.admin_access.exposed_to_internet is False
    assert profile.admin_access.mfa_enabled is False


@pytest.mark.parametrize(
    "description",
    [
        "Админка есть. MFA включена только у клиентов.",
        "Админка есть, MFA включена только у клиентов.",
    ],
)
def test_mfa_for_clients_is_not_attributed_to_admin_access(description: str) -> None:
    profile = extract_architecture_profile(description)

    assert profile.admin_access.exists is True
    assert profile.admin_access.mfa_enabled is None
    assert "admin_mfa" in profile.unknowns


def test_unknown_profile_is_explicit_and_extraction_is_deterministic() -> None:
    first = extract_architecture_profile("Небольшой сервис без подробностей")
    second = extract_architecture_profile("Небольшой сервис без подробностей")

    assert first == second
    assert first.architecture_type is ArchitectureType.unknown
    assert first.exposure is Exposure.unknown
    assert first.storage_location is StorageLocation.unknown
    assert first.unknowns == ["architecture_type", "exposure", "storage_location"]
    assert first.has_payments is None
    assert first.has_logs_or_observability is None


def test_detects_mixed_storage_location() -> None:
    profile = extract_architecture_profile(
        "B2B SaaS. База в России, аналитика отправляется в foreign cloud."
    )

    assert profile.storage_location is StorageLocation.mixed
