"""LLM-based structured architecture extraction.

Uses an LLM to extract structured architecture facts from free-text
descriptions, with Pydantic validation and heuristic fallback.
"""

import json
import logging
import re
from collections.abc import Callable
from typing import Any

from app.core.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.models import ArchitectureProfile
from app.rules.architecture_patterns import extract_architecture_profile

logger = logging.getLogger(__name__)


def _parse_llm_response(response: str) -> dict[str, Any]:
    """Extract JSON from LLM response, handling markdown code blocks."""
    response = response.strip()

    json_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", response, re.DOTALL)
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
        logger.warning("LLM extraction failed, using heuristic fallback: %s", e)
        return extract_architecture_profile(description)
