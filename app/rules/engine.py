"""Deterministic compliance rule engine.

Accepts an ArchitectureProfile and returns a ComplianceAssessment
with regulatory triggers, red flags, recommended controls, and
clarification questions.
"""

from app.models import (
    ArchitectureProfile,
    ArchitectureType,
    ClarificationQuestion,
    ComplianceAssessment,
    Confidence,
    DataCategory,
    IntegrationType,
    RecommendedControl,
    RedFlag,
    RegulatoryTrigger,
    Severity,
)

DEFAULT_DISCLAIMER = (
    "Ответ носит информационный характер и предназначен для предварительной "
    "архитектурной проверки. Он не является юридическим заключением, аудитом ИБ "
    "или заменой консультации профильного специалиста."
)

_INTEGRATION_TYPES_WITH_DATA_RISK = {
    IntegrationType.email_provider,
    IntegrationType.sms_provider,
    IntegrationType.analytics,
    IntegrationType.observability,
    IntegrationType.llm_provider,
    IntegrationType.crm,
    IntegrationType.edo,
}


def _add_trigger(
    triggers: list[RegulatoryTrigger],
    *,
    id: str,
    title: str,
    description: str,
    basis: list[str],
    confidence: Confidence = Confidence.medium,
    reason: str | None = None,
) -> None:
    triggers.append(
        RegulatoryTrigger(
            id=id,
            title=title,
            description=description,
            basis=basis,
            confidence=confidence,
            reason=reason,
        )
    )


def _add_flag(
    flags: list[RedFlag],
    *,
    id: str,
    title: str,
    description: str,
    severity: Severity = Severity.medium,
    reason: str | None = None,
) -> None:
    flags.append(
        RedFlag(id=id, title=title, description=description, severity=severity, reason=reason)
    )


def _add_control(
    controls: list[RecommendedControl],
    *,
    id: str,
    title: str,
    description: str,
    priority: Severity = Severity.medium,
    related_triggers: list[str],
) -> None:
    controls.append(
        RecommendedControl(
            id=id,
            title=title,
            description=description,
            priority=priority,
            related_triggers=related_triggers,
        )
    )


def _add_question(
    questions: list[ClarificationQuestion],
    *,
    id: str,
    question: str,
    reason: str,
    related_triggers: list[str],
) -> None:
    questions.append(
        ClarificationQuestion(
            id=id,
            question=question,
            reason=reason,
            related_triggers=related_triggers,
        )
    )


def _rule_personal_data(profile: ArchitectureProfile, triggers: list[RegulatoryTrigger]) -> bool:
    has_pd = DataCategory.personal_data in profile.data_categories
    if not has_pd:
        return False

    _add_trigger(
        triggers,
        id="personal_data_processing",
        title="Обработка персональных данных",
        description=(
            "Обнаружены признаки обработки персональных данных "
            "(email, телефон, ФИО и др.)."
        ),
        basis=["152-ФЗ"],
        confidence=Confidence.high,
    )
    return True


def _rule_public_saas_with_pd(
    profile: ArchitectureProfile,
    triggers: list[RegulatoryTrigger],
    questions: list[ClarificationQuestion],
    pd_detected: bool,
) -> None:
    if not pd_detected:
        return

    is_public = profile.architecture_type in (
        ArchitectureType.public_saas,
        ArchitectureType.b2b_saas,
    )
    if not is_public:
        return

    _add_trigger(
        triggers,
        id="possible_ispdn",
        title="Возможная ИСПДн",
        description="Система может являться информационной системой персональных данных.",
        basis=["152-ФЗ", "ПП РФ №1119", "Приказ ФСТЭК №21"],
    )

    _add_trigger(
        triggers,
        id="privacy_policy_required",
        title="Требуется политика конфиденциальности",
        description="Публичный сервис с персональными данными требует политики обработки ПДн.",
        basis=["152-ФЗ"],
    )

    _add_trigger(
        triggers,
        id="security_measures_required",
        title="Требуются меры защиты ПДн",
        description="Необходимо обеспечить безопасность персональных данных.",
        basis=["152-ФЗ", "ПП РФ №1119"],
    )

    _add_question(
        questions,
        id="pd_storage_location",
        question="Где физически хранятся персональные данные?",
        reason="Необходимо определить юрисдикцию и применимые требования.",
        related_triggers=["personal_data_processing", "possible_ispdn"],
    )
    _add_question(
        questions,
        id="pd_roskomnadzor_notification",
        question="Уведомлялся ли Роскомнадзор об обработке ПДн?",
        reason="Оператор обязан уведомить Роскомнадзор до начала обработки.",
        related_triggers=["personal_data_processing"],
    )
    _add_question(
        questions,
        id="pd_processing_purpose",
        question="Какие цели обработки определены?",
        reason="Цели обработки должны быть конкретными и законными.",
        related_triggers=["personal_data_processing"],
    )
    _add_question(
        questions,
        id="pd_processing_policy",
        question="Есть ли политика обработки персональных данных?",
        reason="Оператор обязан определить политику в отношении обработки ПДн.",
        related_triggers=["personal_data_processing", "privacy_policy_required"],
    )
    _add_question(
        questions,
        id="pd_access_roles",
        question="Какие роли имеют доступ к ПДн?",
        reason="Доступ к ПДн должен быть ограничен необходимыми сотрудниками.",
        related_triggers=["personal_data_processing", "possible_ispdn"],
    )


def _rule_external_integrations(
    profile: ArchitectureProfile,
    flags: list[RedFlag],
    questions: list[ClarificationQuestion],
    pd_detected: bool,
) -> None:
    if not pd_detected:
        return

    risky_integrations = [
        i for i in profile.integrations
        if i.type in _INTEGRATION_TYPES_WITH_DATA_RISK
        and i.sends_personal_data in (True, None)
    ]
    if not risky_integrations:
        return

    _add_flag(
        flags,
        id="external_processor_or_transfer_unknown",
        title="Передача данных внешнему обработчику",
        description=(
            f"Обнаружены интеграции "
            f"({', '.join(i.name or i.type.value for i in risky_integrations)}), "
            "которые могут получать персональные данные."
        ),
        severity=Severity.high,
    )

    _add_flag(
        flags,
        id="possible_cross_border_transfer",
        title="Возможная трансграничная передача",
        description="Необходимо уточнить расположение внешних сервисов.",
        severity=Severity.medium,
    )

    _add_question(
        questions,
        id="external_pd_transfer",
        question="Передаются ли персональные данные во внешний сервис?",
        reason="Необходимо определить наличие поручения обработки.",
        related_triggers=["personal_data_processing"],
    )
    _add_question(
        questions,
        id="external_service_location",
        question="Где расположен внешний сервис?",
        reason="Возможна трансграничная передача ПДн.",
        related_triggers=["personal_data_processing", "possible_cross_border_transfer"],
    )
    _add_question(
        questions,
        id="external_processing_agreement",
        question="Есть ли договор/поручение обработки?",
        reason="Оператор обязан заключить договор с обработчиком.",
        related_triggers=["personal_data_processing"],
    )
    _add_question(
        questions,
        id="external_pd_disable",
        question="Можно ли отключить передачу ПДн?",
        reason="Следует минимизировать передачу данных третьим сторонам.",
        related_triggers=["personal_data_processing"],
    )


def _rule_observability(
    profile: ArchitectureProfile,
    flags: list[RedFlag],
    controls: list[RecommendedControl],
    pd_detected: bool,
) -> None:
    if not profile.has_logs_or_observability:
        return

    _add_flag(
        flags,
        id="possible_personal_data_in_logs",
        title="Возможные ПДн в логах",
        description=(
            "Логи и observability-сервисы могут содержать персональные данные."
        ),
        severity=Severity.medium,
    )

    _add_control(
        controls,
        id="mask_personal_data_in_logs",
        title="Маскирование ПДн в логах",
        description="Персональные данные должны маскироваться или хешироваться в логах.",
        priority=Severity.high,
        related_triggers=["personal_data_processing"],
    )
    _add_control(
        controls,
        id="restrict_observability_access",
        title="Ограничение доступа к observability",
        description="Доступ к логам должен быть ограничен.",
        priority=Severity.medium,
        related_triggers=["personal_data_processing"],
    )
    _add_control(
        controls,
        id="set_log_retention_policy",
        title="Политика хранения логов",
        description="Необходимо определить сроки хранения и удаления логов.",
        priority=Severity.medium,
        related_triggers=["personal_data_processing"],
    )

    if pd_detected:
        _add_flag(
            flags,
            id="personal_data_in_third_party_services",
            title="ПДн во внешних сервисах",
            description="Персональные данные могут передаваться во внешние observability-сервисы.",
            severity=Severity.high,
        )


def _rule_admin_panel(
    profile: ArchitectureProfile,
    flags: list[RedFlag],
    controls: list[RecommendedControl],
) -> None:
    admin = profile.admin_access
    if not admin.exists:
        return

    if admin.exposed_to_internet:
        _add_flag(
            flags,
            id="internet_exposed_admin_panel",
            title="Админ-панель доступна из интернета",
            description="Административный интерфейс доступен из публичной сети.",
            severity=Severity.high,
        )

    if not admin.mfa_enabled:
        _add_flag(
            flags,
            id="admin_mfa_missing_or_unknown",
            title="MFA для администраторов отсутствует или не подтверждена",
            description="Многофакторная аутентификация для административного доступа не включена.",
            severity=Severity.high,
        )

    _add_control(
        controls,
        id="enable_mfa",
        title="Включить MFA",
        description="Добавить второй фактор для административного доступа.",
        priority=Severity.high,
        related_triggers=["personal_data_processing"],
    )
    _add_control(
        controls,
        id="restrict_admin_by_vpn_or_ip",
        title="Ограничить доступ к админке",
        description="Ограничить административный доступ по VPN или IP-адресам.",
        priority=Severity.high,
        related_triggers=["personal_data_processing"],
    )
    _add_control(
        controls,
        id="enable_admin_audit_log",
        title="Включить аудит действий администраторов",
        description="Все действия администраторов должны логироваться.",
        priority=Severity.medium,
        related_triggers=["personal_data_processing"],
    )
    _add_control(
        controls,
        id="role_based_access_control",
        title="Ролевой доступ",
        description="Реализовать RBAC для административного интерфейса.",
        priority=Severity.medium,
        related_triggers=["personal_data_processing"],
    )


def _rule_payments(
    profile: ArchitectureProfile,
    triggers: list[RegulatoryTrigger],
    questions: list[ClarificationQuestion],
) -> None:
    if not profile.has_payments:
        return

    _add_trigger(
        triggers,
        id="payment_regulation_possible",
        title="Возможное регулирование платежей",
        description="Обнаружены платёжные операции; возможно применение 161-ФЗ.",
        basis=["161-ФЗ", "Bank of Russia requirements"],
    )

    _add_question(
        questions,
        id="payment_provider_identity",
        question="Кто является платёжным провайдером?",
        reason="Необходимо определить применимые требования к платёжной инфраструктуре.",
        related_triggers=["payment_regulation_possible"],
    )
    _add_question(
        questions,
        id="payment_data_storage",
        question="Хранит ли сервис платёжные данные или только получает статусы платежей?",
        reason="Хранение платёжных данных требует дополнительных мер защиты.",
        related_triggers=["payment_regulation_possible"],
    )


def _rule_electronic_signature(
    profile: ArchitectureProfile,
    triggers: list[RegulatoryTrigger],
    questions: list[ClarificationQuestion],
) -> None:
    if not profile.has_electronic_signature:
        return

    _add_trigger(
        triggers,
        id="electronic_signature_regulation",
        title="Регулирование электронной подписи",
        description="Обнаружены признаки использования электронной подписи.",
        basis=["63-ФЗ"],
    )

    _add_question(
        questions,
        id="es_type",
        question="Какой тип электронной подписи используется?",
        reason="Различные типы ЭП имеют разные юридические последствия.",
        related_triggers=["electronic_signature_regulation"],
    )
    _add_question(
        questions,
        id="es_legally_significant",
        question="Есть ли юридически значимые действия?",
        reason="Необходимо определить, создаёт ли ЭП юридические последствия.",
        related_triggers=["electronic_signature_regulation"],
    )
    _add_question(
        questions,
        id="es_user_consent",
        question="Как фиксируется волеизъявление пользователя?",
        reason="Необходимо обеспечить доказуемость согласия пользователя.",
        related_triggers=["electronic_signature_regulation"],
    )


def _rule_commercial_secret(
    profile: ArchitectureProfile,
    triggers: list[RegulatoryTrigger],
    controls: list[RecommendedControl],
) -> None:
    description = profile.source_description.lower()

    commercial_markers = (
        "коммерческая тайна",
        "customer database",
        "internal analytics",
        "source code",
        "financial reports",
        "business reports",
        "technical documentation",
    )
    has_commercial_secret = any(m in description for m in commercial_markers)

    if not has_commercial_secret:
        return

    _add_trigger(
        triggers,
        id="commercial_secret_possible",
        title="Возможная коммерческая тайна",
        description="Обнаружены признаки обработки коммерческой тайны.",
        basis=["98-ФЗ"],
    )

    _add_control(
        controls,
        id="classify_sensitive_business_data",
        title="Классификация конфиденциальных данных",
        description="Необходимо классифицировать бизнес-данные по уровню чувствительности.",
        priority=Severity.medium,
        related_triggers=["commercial_secret_possible"],
    )
    _add_control(
        controls,
        id="restrict_access_to_commercial_secret",
        title="Ограничение доступа к коммерческой тайне",
        description="Доступ к коммерческой тайне должен быть ограничен.",
        priority=Severity.high,
        related_triggers=["commercial_secret_possible"],
    )
    _add_control(
        controls,
        id="audit_access_to_sensitive_documents",
        title="Аудит доступа к敏感ительным документам",
        description="Все обращения к конфиденциальным документам должны логироваться.",
        priority=Severity.medium,
        related_triggers=["commercial_secret_possible"],
    )


def _rule_kii(
    profile: ArchitectureProfile,
    triggers: list[RegulatoryTrigger],
    questions: list[ClarificationQuestion],
) -> None:
    if not profile.serves_kii_subject:
        return

    _add_trigger(
        triggers,
        id="kii_relevance_possible",
        title="Возможная релевантность КИИ",
        description="Система может быть связана с критической информационной инфраструктурой.",
        basis=["187-ФЗ"],
    )

    _add_question(
        questions,
        id="kii_subject_status",
        question=(
            "Является ли заказчик субъектом КИИ? Является ли система значимым объектом КИИ "
            "или частью такого объекта?"
        ),
        reason="Субъекты КИИ обязаны выполнить категорирование и обеспечить защиту.",
        related_triggers=["kii_relevance_possible"],
    )


def analyze_profile(profile: ArchitectureProfile) -> ComplianceAssessment:
    """Analyze an ArchitectureProfile and produce a ComplianceAssessment.

    Deterministic rule-based analysis without LLM or external services.
    """
    triggers: list[RegulatoryTrigger] = []
    flags: list[RedFlag] = []
    controls: list[RecommendedControl] = []
    questions: list[ClarificationQuestion] = []

    pd_detected = _rule_personal_data(profile, triggers)
    _rule_public_saas_with_pd(profile, triggers, questions, pd_detected)
    _rule_external_integrations(profile, flags, questions, pd_detected)
    _rule_observability(profile, flags, controls, pd_detected)
    _rule_admin_panel(profile, flags, controls)
    _rule_payments(profile, triggers, questions)
    _rule_electronic_signature(profile, triggers, questions)
    _rule_commercial_secret(profile, triggers, controls)
    _rule_kii(profile, triggers, questions)

    summary_parts: list[str] = []
    if pd_detected:
        summary_parts.append(
            "Обнаружены признаки обработки персональных данных."
        )
    if profile.has_logs_or_observability:
        summary_parts.append(
            "Присутствует логирование/observability; необходимо проверить наличие ПДн в логах."
        )
    if profile.admin_access.exists and profile.admin_access.exposed_to_internet:
        summary_parts.append(
            "Административный интерфейс доступен из интернета; требуется проверить меры защиты."
        )
    if profile.has_payments:
        summary_parts.append(
            "Обнаружены платёжные операции; возможно применимо регулирование 161-ФЗ."
        )
    if not summary_parts:
        summary_parts.append(
            "Значимых регуляторных триггеров не обнаружено. Рекомендуется ручная проверка."
        )

    summary = " ".join(summary_parts)

    return ComplianceAssessment(
        architecture_profile=profile,
        summary=summary,
        regulatory_triggers=triggers,
        red_flags=flags,
        recommended_controls=controls,
        clarification_questions=questions,
        disclaimer=DEFAULT_DISCLAIMER,
    )
