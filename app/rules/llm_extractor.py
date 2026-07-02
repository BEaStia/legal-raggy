"""LLM-based structured architecture extraction.

Uses an LLM to extract structured architecture facts from free-text
descriptions, with Pydantic validation and heuristic fallback.
"""

import json
import logging
import re
from collections.abc import Callable
from typing import Any

from app.models import ArchitectureProfile
from app.rules.architecture_patterns import extract_architecture_profile

logger = logging.getLogger(__name__)

_ARCH_TYPES = [
    "public_website", "public_saas", "b2b_saas", "internal_service",
    "mobile_backend", "integration_api", "dwh_bi", "ml_ai_pipeline",
    "payment_service", "edo_signature_service", "unknown",
]
_EXPOSURE_TYPES = [
    "public_internet", "vpn", "internal_network", "closed_contour",
    "hybrid", "unknown",
]
_DATA_CATS = [
    "personal_data", "special_personal_data", "biometric_personal_data",
    "authentication_secret", "payment_data", "commercial_secret",
    "telemetry_logs", "behavioral_data", "documents", "source_code",
    "unknown",
]
_INT_TYPES = [
    "payment_provider", "email_provider", "sms_provider", "analytics",
    "observability", "llm_provider", "crm", "edo", "government_system",
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
    "- integrations: list of {name, type, sends_personal_data, location}\n"
    f"  - type: one of {_INT_TYPES}\n"
    "- admin_access: {exists, exposed_to_internet, mfa_enabled}\n"
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

USER_PROMPT_TEMPLATE = (
    "Extract architecture facts from this description:\n\n"
    "{description}"
)


def _parse_llm_response(response: str) -> dict[str, Any]:
    """Extract JSON from LLM response, handling markdown code blocks."""
    response = response.strip()

    json_match = re.search(
        r"```(?:json)?\s*\n(.*?)\n```", response, re.DOTALL
    )
    if json_match:
        response = json_match.group(1)

    return json.loads(response)


def _safe_coerce(data: dict[str, Any]) -> dict[str, Any]:
    """Coerce LLM output to match ArchitectureProfile expectations."""
    if "integrations" not in data or data["integrations"] is None:
        data["integrations"] = []

    if "admin_access" not in data or data["admin_access"] is None:
        data["admin_access"] = {}

    return data


def extract_with_llm(
    description: str,
    llm_fn: Callable[[str, str], str] | None = None,
) -> ArchitectureProfile:
    """Extract architecture profile using LLM with heuristic fallback.

    Args:
        description: Architecture description text.
        llm_fn: Optional callable(system_prompt, user_prompt) -> str.
                If None, falls back to heuristic extractor.

    Returns:
        ArchitectureProfile from LLM or heuristic fallback.
    """
    if llm_fn is None:
        logger.info("No LLM function provided, using heuristic fallback")
        return extract_architecture_profile(description)

    try:
        user_prompt = USER_PROMPT_TEMPLATE.format(description=description)
        response = llm_fn(SYSTEM_PROMPT, user_prompt)
        data = _parse_llm_response(response)
        data = _safe_coerce(data)
        return ArchitectureProfile(
            source_description=description,
            **data,
        )
    except Exception as e:
        logger.warning(
            "LLM extraction failed, using heuristic fallback: %s", e
        )
        return extract_architecture_profile(description)
