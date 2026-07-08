"""Prompt definitions for LLM-based architecture extraction.

Prompts are defined here for easy iteration without touching code.
"""

_ARCH_TYPES = [
    "public_website",
    "public_saas",
    "b2b_saas",
    "internal_service",
    "mobile_backend",
    "integration_api",
    "dwh_bi",
    "ml_ai_pipeline",
    "payment_service",
    "edo_signature_service",
    "unknown",
]
_EXPOSURE_TYPES = [
    "public_internet",
    "vpn",
    "internal_network",
    "closed_contour",
    "hybrid",
    "unknown",
]
_DATA_CATS = [
    "personal_data",
    "special_personal_data",
    "biometric_personal_data",
    "authentication_secret",
    "payment_data",
    "commercial_secret",
    "telemetry_logs",
    "behavioral_data",
    "documents",
    "source_code",
    "unknown",
]
_INT_TYPES = [
    "payment_provider",
    "email_provider",
    "sms_provider",
    "analytics",
    "observability",
    "llm_provider",
    "crm",
    "edo",
    "government_system",
    "unknown",
]

SYSTEM_PROMPT = (
    "You are an IT architecture analyst. "
    "Extract structured facts from the architecture description.\n\n"
    "Return ONLY a valid JSON object with these fields:\n"
    f"- architecture_type: one of {_ARCH_TYPES}\n"
    f"- exposure: one of {_EXPOSURE_TYPES}\n"
    "- users: list of user types mentioned\n"
    f"- data_categories: list of {_DATA_CATS}\n"
    "- raw_data_items: list of specific data items\n"
    "- storage_location: one of [russia, foreign, mixed, unknown]\n"
    "- integrations: list of {{name, type, sends_personal_data, location}}\n"
    f"  - type: one of {_INT_TYPES}\n"
    "- admin_access: {{exists, exposed_to_internet, mfa_enabled}}\n"
    "- has_payments: boolean or null\n"
    "- has_electronic_signature: boolean or null\n"
    "- has_ml_or_ai_processing: boolean or null\n"
    "- has_logs_or_observability: boolean or null\n"
    "- has_backups: boolean or null\n"
    "- serves_kii_subject: boolean or null\n"
    "- serves_government: boolean or null\n"
    "- unknowns: list of important missing information\n\n"
    "Rules:\n"
    "- Use null for unknown booleans\n"
    "- Only include data_categories actually mentioned\n"
    '- Be conservative: prefer "unknown" over guessing\n'
    "- Return valid JSON only, no markdown, no explanations"
)

USER_PROMPT_TEMPLATE = "Extract architecture facts from this description:\n\n{description}"
