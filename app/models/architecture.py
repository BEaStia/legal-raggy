from enum import Enum

from pydantic import BaseModel, Field


class Exposure(str, Enum):
    public_internet = "public_internet"
    vpn = "vpn"
    internal_network = "internal_network"
    closed_contour = "closed_contour"
    hybrid = "hybrid"
    unknown = "unknown"


class ArchitectureType(str, Enum):
    public_website = "public_website"
    public_saas = "public_saas"
    b2b_saas = "b2b_saas"
    internal_service = "internal_service"
    mobile_backend = "mobile_backend"
    integration_api = "integration_api"
    dwh_bi = "dwh_bi"
    ml_ai_pipeline = "ml_ai_pipeline"
    payment_service = "payment_service"
    edo_signature_service = "edo_signature_service"
    unknown = "unknown"


class DataCategory(str, Enum):
    personal_data = "personal_data"
    special_personal_data = "special_personal_data"
    biometric_personal_data = "biometric_personal_data"
    authentication_secret = "authentication_secret"
    payment_data = "payment_data"
    commercial_secret = "commercial_secret"
    telemetry_logs = "telemetry_logs"
    behavioral_data = "behavioral_data"
    documents = "documents"
    source_code = "source_code"
    unknown = "unknown"


class StorageLocation(str, Enum):
    russia = "russia"
    foreign = "foreign"
    mixed = "mixed"
    unknown = "unknown"


class IntegrationType(str, Enum):
    payment_provider = "payment_provider"
    email_provider = "email_provider"
    sms_provider = "sms_provider"
    analytics = "analytics"
    observability = "observability"
    llm_provider = "llm_provider"
    crm = "crm"
    edo = "edo"
    government_system = "government_system"
    unknown = "unknown"


class Integration(BaseModel):
    name: str | None = None
    type: IntegrationType = IntegrationType.unknown
    sends_personal_data: bool | None = None
    location: StorageLocation = StorageLocation.unknown
    notes: str | None = None


class AdminAccess(BaseModel):
    exists: bool | None = None
    exposed_to_internet: bool | None = None
    mfa_enabled: bool | None = None
    audit_log_enabled: bool | None = None
    role_based_access: bool | None = None


class ArchitectureProfile(BaseModel):
    source_description: str

    architecture_type: ArchitectureType = ArchitectureType.unknown
    exposure: Exposure = Exposure.unknown

    users: list[str] = Field(default_factory=list)
    data_categories: list[DataCategory] = Field(default_factory=list)
    raw_data_items: list[str] = Field(default_factory=list)

    storage_location: StorageLocation = StorageLocation.unknown
    integrations: list[Integration] = Field(default_factory=list)

    admin_access: AdminAccess = Field(default_factory=AdminAccess)

    has_payments: bool | None = None
    has_electronic_signature: bool | None = None
    has_ml_or_ai_processing: bool | None = None
    has_logs_or_observability: bool | None = None
    has_backups: bool | None = None
    serves_kii_subject: bool | None = None
    serves_government: bool | None = None

    unknowns: list[str] = Field(default_factory=list)
