"""Golden dataset for compliance evaluation."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GoldenCase:
    """A single test case with expected outputs."""

    id: str
    description: str
    expected_architecture_type: str
    expected_data_categories: list[str] = field(default_factory=list)
    expected_triggers: list[str] = field(default_factory=list)
    expected_red_flags: list[str] = field(default_factory=list)
    expected_controls: list[str] = field(default_factory=list)
    expected_has_payments: bool | None = None
    expected_has_electronic_signature: bool | None = None


GOLDEN_DATASET: list[GoldenCase] = [
    # 1. B2B SaaS with personal data
    GoldenCase(
        id="case_01",
        description=(
            "B2B SaaS для клиентов. Регистрация по email и телефону. "
            "Админка доступна из интернета, MFA нет. База в РФ."
        ),
        expected_architecture_type="b2b_saas",
        expected_data_categories=["personal_data"],
        expected_triggers=["personal_data_processing", "possible_ispdn"],
        expected_red_flags=["internet_exposed_admin_panel"],
        expected_controls=["enable_mfa"],
    ),
    # 2. Public website with analytics
    GoldenCase(
        id="case_02",
        description=(
            "Публичный сайт с Google Analytics и формой обратной связи. "
            "Собираем email и имя."
        ),
        expected_architecture_type="public_website",
        expected_data_categories=["personal_data"],
        expected_triggers=["personal_data_processing"],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 3. Internal service with commercial secret
    GoldenCase(
        id="case_03",
        description=(
            "Внутренний сервис для хранения source code и financial reports. "
            "Доступ только по VPN. Это коммерческая тайна."
        ),
        expected_architecture_type="internal_service",
        expected_data_categories=["commercial_secret", "source_code"],
        expected_triggers=["commercial_secret_possible"],
        expected_red_flags=[],
        expected_controls=["restrict_access_to_commercial_secret"],
    ),
    # 4. Payment service
    GoldenCase(
        id="case_04",
        description=(
            "Сервис оплаты подписки через платежный провайдер. "
            "Храним статусы платежей."
        ),
        expected_architecture_type="payment_service",
        expected_data_categories=["payment_data"],
        expected_triggers=["payment_regulation_possible"],
        expected_red_flags=[],
        expected_controls=[],
        expected_has_payments=True,
    ),
    # 5. EDO service with electronic signature
    GoldenCase(
        id="case_05",
        description=(
            "Сервис ЭДО с УКЭП для юридически значимых документов."
        ),
        expected_architecture_type="edo_signature_service",
        expected_data_categories=["documents"],
        expected_triggers=["electronic_signature_regulation"],
        expected_red_flags=[],
        expected_controls=[],
        expected_has_electronic_signature=True,
    ),
    # 6. ML/AI pipeline with personal data
    GoldenCase(
        id="case_06",
        description=(
            "ML pipeline для обработки персональных данных клиентов. "
            "Тренируем модели на исторических данных."
        ),
        expected_architecture_type="ml_ai_pipeline",
        expected_data_categories=["personal_data"],
        expected_triggers=["personal_data_processing"],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 7. Integration API
    GoldenCase(
        id="case_07",
        description=(
            "API интеграция с CRM и email provider. "
            "Передаём email и имя клиентов."
        ),
        expected_architecture_type="integration_api",
        expected_data_categories=["personal_data"],
        expected_triggers=["personal_data_processing"],
        expected_red_flags=["external_processor_or_transfer_unknown"],
        expected_controls=[],
    ),
    # 8. KII subject service
    GoldenCase(
        id="case_08",
        description=(
            "Сервис для банка. Является частью КИИ субъекта."
        ),
        expected_architecture_type="unknown",
        expected_data_categories=[],
        expected_triggers=["kii_relevance_possible"],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 9. Observability stack
    GoldenCase(
        id="case_09",
        description=(
            "Логи уходят в Sentry и Grafana. Там может быть email."
        ),
        expected_architecture_type="unknown",
        expected_data_categories=["personal_data", "telemetry_logs"],
        expected_triggers=["personal_data_processing"],
        expected_red_flags=["possible_personal_data_in_logs"],
        expected_controls=["mask_personal_data_in_logs"],
    ),
    # 10. Hybrid architecture
    GoldenCase(
        id="case_10",
        description=(
            "Гибридная архитектура: публичный SaaS + internal service. "
            "Данные пользователей в РФ, аналитика во внешнем сервисе."
        ),
        expected_architecture_type="b2b_saas",
        expected_data_categories=["personal_data"],
        expected_triggers=["personal_data_processing", "possible_ispdn"],
        expected_red_flags=["external_processor_or_transfer_unknown"],
        expected_controls=[],
    ),
    # 11. Minimal service
    GoldenCase(
        id="case_11",
        description="Простой internal service без персональных данных.",
        expected_architecture_type="internal_service",
        expected_data_categories=[],
        expected_triggers=[],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 12. Mobile backend
    GoldenCase(
        id="case_12",
        description=(
            "Mobile backend для iOS/Android. "
            "Пользователи регистрируются по email."
        ),
        expected_architecture_type="mobile_backend",
        expected_data_categories=["personal_data"],
        expected_triggers=["personal_data_processing"],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 13. DWH/BI with commercial data
    GoldenCase(
        id="case_13",
        description=(
            "DWH для хранения business reports и internal analytics."
        ),
        expected_architecture_type="dwh_bi",
        expected_data_categories=["commercial_secret"],
        expected_triggers=["commercial_secret_possible"],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 14. Public SaaS with MFA
    GoldenCase(
        id="case_14",
        description=(
            "Public SaaS с MFA для админки. "
            "Регистрация по email. База в РФ."
        ),
        expected_architecture_type="public_saas",
        expected_data_categories=["personal_data"],
        expected_triggers=["personal_data_processing"],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 15. Government service
    GoldenCase(
        id="case_15",
        description=(
            "Сервис для госоргана. Интеграция с government system."
        ),
        expected_architecture_type="unknown",
        expected_data_categories=[],
        expected_triggers=[],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 16. EDO without signature
    GoldenCase(
        id="case_16",
        description="Сервис документооборота без электронной подписи.",
        expected_architecture_type="edo_signature_service",
        expected_data_categories=["documents"],
        expected_triggers=[],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 17. Payment with personal data
    GoldenCase(
        id="case_17",
        description=(
            "Платежный сервис с хранением email и имени плательщика."
        ),
        expected_architecture_type="payment_service",
        expected_data_categories=["personal_data", "payment_data"],
        expected_triggers=["personal_data_processing", "payment_regulation_possible"],
        expected_red_flags=[],
        expected_controls=[],
        expected_has_payments=True,
    ),
    # 18. ML with no personal data
    GoldenCase(
        id="case_18",
        description="ML pipeline для обработки анонимизированных данных.",
        expected_architecture_type="ml_ai_pipeline",
        expected_data_categories=[],
        expected_triggers=[],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 19. Integration with observability
    GoldenCase(
        id="case_19",
        description=(
            "API интеграция с observability service. "
            "Передаём логи без персональных данных."
        ),
        expected_architecture_type="integration_api",
        expected_data_categories=["telemetry_logs"],
        expected_triggers=[],
        expected_red_flags=[],
        expected_controls=[],
    ),
    # 20. Complex B2B SaaS
    GoldenCase(
        id="case_20",
        description=(
            "B2B SaaS с платежами, ЭДО и интеграцией с CRM. "
            "Админка из интернета без MFA. Логи в Sentry."
        ),
        expected_architecture_type="b2b_saas",
        expected_data_categories=["personal_data", "payment_data"],
        expected_triggers=[
            "personal_data_processing",
            "possible_ispdn",
            "payment_regulation_possible",
            "electronic_signature_regulation",
        ],
        expected_red_flags=[
            "internet_exposed_admin_panel",
            "admin_mfa_missing_or_unknown",
        ],
        expected_controls=["enable_mfa"],
        expected_has_payments=True,
        expected_has_electronic_signature=True,
    ),
]
