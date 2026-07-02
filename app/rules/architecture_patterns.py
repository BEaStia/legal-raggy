import re
import unicodedata

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


def _normalize(description: str) -> str:
    normalized = unicodedata.normalize("NFKC", description).casefold().replace("ё", "е")
    return " ".join(normalized.split())


def _contains(text: str, *terms: str) -> bool:
    return any(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) for term in terms)


def _has_admin_marker(text: str) -> bool:
    return _contains(
        text,
        "админка",
        "админки",
        "админ-панель",
        "admin panel",
        "admin console",
        "administrator",
        "administrators",
    )


def _detect_architecture_type(text: str) -> ArchitectureType:
    if _contains(text, "b2b") and _contains(text, "saas"):
        return ArchitectureType.b2b_saas
    if _contains(text, "публичный сайт", "public website"):
        return ArchitectureType.public_website
    if _contains(text, "saas"):
        return ArchitectureType.public_saas
    if _contains(text, "internal service", "внутренний сервис"):
        return ArchitectureType.internal_service
    if _contains(text, "мобильное приложение", "mobile app"):
        return ArchitectureType.mobile_backend
    if _contains(text, "api", "webhook"):
        return ArchitectureType.integration_api
    if _contains(text, "dwh", "bi", "хранилище данных"):
        return ArchitectureType.dwh_bi
    if _contains(text, "ml pipeline", "ai pipeline"):
        return ArchitectureType.ml_ai_pipeline
    if _contains(text, "платежный сервис", "payment service"):
        return ArchitectureType.payment_service
    if _contains(text, "эдо", "электронная подпись"):
        return ArchitectureType.edo_signature_service
    return ArchitectureType.unknown


def _has_public_exposure_negation(text: str) -> bool:
    return _contains(
        text,
        "без доступа в интернет",
        "не доступен из интернета",
        "не доступна из интернета",
        "недоступен из интернета",
        "недоступна из интернета",
        "not available on public internet",
        "not accessible from public internet",
        "not exposed to public internet",
        "no public internet access",
    )


def _has_public_exposure(text: str) -> bool:
    return _contains(
        text,
        "интернет",
        "публичный сайт",
        "public internet",
        "public website",
        "доступна из интернета",
        "доступен из интернета",
    ) and not _has_public_exposure_negation(text)


def _detect_exposure(text: str) -> Exposure:
    if _contains(text, "закрытый контур", "закрытом контуре", "closed contour"):
        return Exposure.closed_contour
    if _has_public_exposure(text):
        return Exposure.public_internet
    if _contains(text, "vpn"):
        return Exposure.vpn
    if _contains(text, "внутренняя сеть", "внутренней сети", "internal network"):
        return Exposure.internal_network
    return Exposure.unknown


def _detect_raw_data_items(text: str) -> list[str]:
    rules = (
        ("email", ("email", "e-mail", "почта", "электронная почта")),
        ("phone", ("телефон", "телефону", "phone")),
        ("full_name", ("фио", "имя", "фамилия", "full name")),
        ("passport", ("паспорт", "passport")),
        ("address", ("адрес", "address")),
        ("ip", ("ip", "ip-адрес", "ip address")),
        ("cookie", ("cookie", "cookies", "куки")),
        ("device_id", ("device id", "идентификатор устройства")),
    )
    return [name for name, terms in rules if _contains(text, *terms)]


def _has_personal_data(text: str, raw_data_items: list[str]) -> bool:
    explicit_negation = _contains(
        text,
        "без персональных данных",
        "без пользовательских данных",
        "не обрабатывает персональные данные",
        "does not process personal data",
    )
    marker = bool(raw_data_items) or _contains(
        text,
        "персональные данные",
        "personal data",
        "пользователь",
        "пользователи",
        "пользователя",
        "аккаунт",
        "личный кабинет",
    )
    return marker and not explicit_negation


def _detect_storage_location(text: str) -> StorageLocation:
    in_russia = _contains(
        text,
        "россия",
        "россии",
        "рф",
        "российское облако",
        "российском облаке",
        "russia",
    )
    abroad = _contains(text, "за рубежом", "иностранное облако", "foreign cloud", "outside russia")
    if in_russia and abroad:
        return StorageLocation.mixed
    if in_russia:
        return StorageLocation.russia
    if abroad:
        return StorageLocation.foreign
    return StorageLocation.unknown


def _detect_integrations(text: str) -> list[Integration]:
    integrations: list[Integration] = []
    observability_rules = (
        ("Sentry", ("sentry",)),
        ("Grafana", ("grafana",)),
        ("Prometheus", ("prometheus",)),
        ("ELK", ("elk",)),
        ("Datadog", ("datadog",)),
    )
    for name, terms in observability_rules:
        if _contains(text, *terms):
            sends_personal_data = None
            if name == "Sentry" and _contains(
                text,
                "туда может попадать",
                "персональные данные отправляются в sentry",
                "personal data is sent to sentry",
            ):
                sends_personal_data = True
            integrations.append(
                Integration(
                    name=name,
                    type=IntegrationType.observability,
                    sends_personal_data=sends_personal_data,
                )
            )

    integration_rules = (
        ("Yandex Metrica", IntegrationType.analytics, ("метрика", "yandex metrica")),
        ("Google Analytics", IntegrationType.analytics, ("google analytics",)),
        ("Email provider", IntegrationType.email_provider, ("email provider",)),
        ("SMS provider", IntegrationType.sms_provider, ("sms provider",)),
        ("CRM", IntegrationType.crm, ("crm",)),
        ("OpenAI", IntegrationType.llm_provider, ("openai",)),
        ("YandexGPT", IntegrationType.llm_provider, ("yandexgpt",)),
        (
            "Payment provider",
            IntegrationType.payment_provider,
            ("платежный провайдер", "payment provider"),
        ),
    )
    for name, integration_type, integration_terms in integration_rules:
        if _contains(text, *integration_terms):
            integrations.append(Integration(name=name, type=integration_type))
    return integrations


def _detect_admin_access(text: str) -> AdminAccess:
    admin_absent = _contains(
        text,
        "админки нет",
        "без админки",
        "нет админки",
        "no admin panel",
    )
    admin_exists = _has_admin_marker(text)
    exists = False if admin_absent else True if admin_exists else None

    exposed_to_internet: bool | None = None
    if exists:
        sentences = re.split(r"[.!?;\n]+", text)
        admin_sentences = [sentence for sentence in sentences if _has_admin_marker(sentence)]
        if any(_has_public_exposure_negation(sentence) for sentence in admin_sentences):
            exposed_to_internet = False
        elif any(_has_public_exposure(sentence) for sentence in admin_sentences):
            exposed_to_internet = True

    mfa_enabled = _detect_admin_mfa(text) if exists else None

    return AdminAccess(
        exists=exists,
        exposed_to_internet=exposed_to_internet,
        mfa_enabled=mfa_enabled,
        audit_log_enabled=True
        if _contains(text, "audit log включен", "аудит действий включен")
        else None,
        role_based_access=True if _contains(text, "rbac", "ролевой доступ") else None,
    )


def _detect_admin_mfa(text: str) -> bool | None:
    sentences = [sentence.strip() for sentence in re.split(r"[.!?;\n]+", text) if sentence.strip()]
    for index, sentence in enumerate(sentences):
        if not _contains(sentence, "mfa", "2fa"):
            continue

        other_subject = _contains(
            sentence,
            "клиент",
            "клиенты",
            "клиентов",
            "пользователь",
            "пользователи",
            "users",
            "clients",
            "customers",
        )
        follows_admin_sentence = index > 0 and _has_admin_marker(sentences[index - 1])
        if other_subject:
            continue
        if not _has_admin_marker(sentence) and not follows_admin_sentence:
            continue

        if _contains(
            sentence,
            "mfa нет",
            "mfa пока нет",
            "без mfa",
            "2fa нет",
            "без 2fa",
            "mfa отсутствует",
            "mfa не используется",
            "no mfa",
            "mfa disabled",
        ):
            return False
        if _contains(
            sentence,
            "mfa включена",
            "mfa включен",
            "2fa включена",
            "2fa enabled",
            "mfa enabled",
        ):
            return True
    return None


def extract_architecture_profile(description: str) -> ArchitectureProfile:
    """Extract a deterministic, preliminary architecture profile from free text."""
    text = _normalize(description)
    architecture_type = _detect_architecture_type(text)
    exposure = _detect_exposure(text)
    raw_data_items = _detect_raw_data_items(text)
    storage_location = _detect_storage_location(text)
    integrations = _detect_integrations(text)
    admin_access = _detect_admin_access(text)

    has_payments: bool | None = None
    if _contains(
        text,
        "оплата",
        "оплаты",
        "платежи",
        "платежный провайдер",
        "эквайринг",
        "касса",
        "payment provider",
    ):
        has_payments = True
    elif _contains(text, "без платежей", "без оплаты", "does not accept payments"):
        has_payments = False

    has_logs_or_observability: bool | None = None
    if _contains(text, "без логов", "логирование отключено", "no logs", "logging disabled"):
        has_logs_or_observability = False
    elif _contains(
        text,
        "логи",
        "logs",
        "логирование",
        "observability",
        "sentry",
        "grafana",
        "prometheus",
        "elk",
        "datadog",
    ):
        has_logs_or_observability = True

    data_categories: list[DataCategory] = []
    if _has_personal_data(text, raw_data_items):
        data_categories.append(DataCategory.personal_data)
    if has_payments:
        data_categories.append(DataCategory.payment_data)
    if has_logs_or_observability:
        data_categories.append(DataCategory.telemetry_logs)

    users: list[str] = []
    if _contains(text, "клиент", "клиенты", "customers"):
        users.append("clients")
    if _contains(text, "пользователь", "пользователи", "users"):
        users.append("users")

    unknowns: list[str] = []
    if architecture_type is ArchitectureType.unknown:
        unknowns.append("architecture_type")
    if exposure is Exposure.unknown:
        unknowns.append("exposure")
    if storage_location is StorageLocation.unknown:
        unknowns.append("storage_location")
    if admin_access.exists:
        if admin_access.exposed_to_internet is None:
            unknowns.append("admin_exposure")
        if admin_access.mfa_enabled is None:
            unknowns.append("admin_mfa")

    return ArchitectureProfile(
        source_description=description,
        architecture_type=architecture_type,
        exposure=exposure,
        users=users,
        data_categories=data_categories,
        raw_data_items=raw_data_items,
        storage_location=storage_location,
        integrations=integrations,
        admin_access=admin_access,
        has_payments=has_payments,
        has_electronic_signature=True
        if _contains(text, "электронная подпись", "укэп", "нэп", "пэп", "эдо")
        else None,
        has_ml_or_ai_processing=True
        if _contains(text, "машинное обучение", "ml", "ai", "llm", "openai", "yandexgpt")
        else None,
        has_logs_or_observability=has_logs_or_observability,
        has_backups=True
        if _contains(text, "backup", "backups", "резервные копии", "резервное копирование")
        else None,
        serves_kii_subject=True
        if _contains(text, "кии", "критическая информационная инфраструктура", "субъект кии")
        else None,
        serves_government=True
        if _contains(text, "государственная система", "государственный заказчик", "government")
        else None,
        unknowns=unknowns,
    )
