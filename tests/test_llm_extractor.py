"""Tests for LLM-based architecture extraction."""

import json
from unittest.mock import MagicMock

import pytest

from app.models import ArchitectureProfile, ArchitectureType, Exposure
from app.rules.llm_extractor import (
    _parse_llm_response,
    _safe_coerce,
    extract_with_llm,
)


def _valid_llm_response(overrides: dict | None = None) -> str:
    """Generate a valid LLM JSON response."""
    data = {
        "architecture_type": "b2b_saas",
        "exposure": "public_internet",
        "users": ["business users", "admins"],
        "data_categories": ["personal_data", "telemetry_logs"],
        "raw_data_items": ["email", "phone"],
        "storage_location": "russia",
        "integrations": [
            {
                "name": "Sentry",
                "type": "observability",
                "sends_personal_data": True,
                "location": "foreign",
                "notes": None,
            }
        ],
        "admin_access": {
            "exists": True,
            "exposed_to_internet": True,
            "mfa_enabled": False,
            "audit_log_enabled": None,
            "role_based_access": None,
        },
        "has_payments": None,
        "has_electronic_signature": None,
        "has_ml_or_ai_processing": None,
        "has_logs_or_observability": True,
        "has_backups": None,
        "serves_kii_subject": None,
        "serves_government": None,
        "unknowns": ["backup strategy"],
    }
    if overrides:
        data.update(overrides)
    return json.dumps(data)


class TestParseLlmResponse:
    def test_parses_plain_json(self) -> None:
        response = '{"architecture_type": "b2b_saas"}'
        result = _parse_llm_response(response)
        assert result["architecture_type"] == "b2b_saas"

    def test_parses_markdown_code_block(self) -> None:
        response = '```json\n{"architecture_type": "public_saas"}\n```'
        result = _parse_llm_response(response)
        assert result["architecture_type"] == "public_saas"

    def test_parses_code_block_without_language(self) -> None:
        response = '```\n{"exposure": "vpn"}\n```'
        result = _parse_llm_response(response)
        assert result["exposure"] == "vpn"

    def test_raises_on_invalid_json(self) -> None:
        with pytest.raises(json.JSONDecodeError):
            _parse_llm_response("not json")


class TestSafeCoerce:
    def test_adds_missing_integrations(self) -> None:
        data: dict = {}
        result = _safe_coerce(data)
        assert result["integrations"] == []

    def test_adds_missing_admin_access(self) -> None:
        data: dict = {}
        result = _safe_coerce(data)
        assert result["admin_access"] == {}

    def test_preserves_none_for_booleans(self) -> None:
        data = {"has_payments": None}
        result = _safe_coerce(data)
        assert result["has_payments"] is None

    def test_preserves_existing_values(self) -> None:
        data = {
            "integrations": [{"name": "test"}],
            "admin_access": {"exists": True},
        }
        result = _safe_coerce(data)
        assert len(result["integrations"]) == 1
        assert result["admin_access"]["exists"] is True


class TestExtractWithLlm:
    def test_uses_llm_when_provided(self) -> None:
        mock_llm = MagicMock(return_value=_valid_llm_response())
        result = extract_with_llm("test description", llm_fn=mock_llm)
        assert isinstance(result, ArchitectureProfile)
        assert result.architecture_type == ArchitectureType.b2b_saas
        assert result.exposure == Exposure.public_internet

    def test_fallback_when_llm_fn_none(self) -> None:
        result = extract_with_llm(
            "B2B SaaS, email registration, admin panel exposed"
        )
        assert isinstance(result, ArchitectureProfile)
        assert result.architecture_type == ArchitectureType.b2b_saas

    def test_fallback_on_llm_error(self) -> None:
        mock_llm = MagicMock(side_effect=Exception("API error"))
        result = extract_with_llm("test", llm_fn=mock_llm)
        assert isinstance(result, ArchitectureProfile)

    def test_fallback_on_invalid_json(self) -> None:
        mock_llm = MagicMock(return_value="not json at all")
        result = extract_with_llm("test", llm_fn=mock_llm)
        assert isinstance(result, ArchitectureProfile)

    def test_fallback_on_pydantic_validation_error(self) -> None:
        mock_llm = MagicMock(
            return_value=json.dumps({
                "architecture_type": "invalid_type",
                "exposure": "invalid_exposure",
            })
        )
        result = extract_with_llm("test", llm_fn=mock_llm)
        assert isinstance(result, ArchitectureProfile)

    def test_parses_integrations_from_llm(self) -> None:
        mock_llm = MagicMock(return_value=_valid_llm_response())
        result = extract_with_llm("test", llm_fn=mock_llm)
        assert len(result.integrations) == 1
        assert result.integrations[0].name == "Sentry"

    def test_parses_admin_access_from_llm(self) -> None:
        mock_llm = MagicMock(return_value=_valid_llm_response())
        result = extract_with_llm("test", llm_fn=mock_llm)
        assert result.admin_access.exists is True
        assert result.admin_access.exposed_to_internet is True
        assert result.admin_access.mfa_enabled is False

    def test_preserves_source_description(self) -> None:
        mock_llm = MagicMock(return_value=_valid_llm_response())
        desc = "My architecture description"
        result = extract_with_llm(desc, llm_fn=mock_llm)
        assert result.source_description == desc

    def test_handles_markdown_code_blocks(self) -> None:
        mock_llm = MagicMock(
            return_value=f"```json\n{_valid_llm_response()}\n```"
        )
        result = extract_with_llm("test", llm_fn=mock_llm)
        assert result.architecture_type == ArchitectureType.b2b_saas
