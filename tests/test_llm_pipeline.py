"""Tests for LLM integration in analysis pipeline."""

import json
from unittest.mock import MagicMock, patch

from app.core.config import Settings
from app.core.llm_provider import create_llm_fn
from app.models import ArchitectureType, Exposure
from app.services.analyze import run_analysis


def _valid_llm_response(overrides: dict | None = None) -> str:
    data = {
        "architecture_type": "b2b_saas",
        "exposure": "public_internet",
        "users": ["business users"],
        "data_categories": ["personal_data"],
        "raw_data_items": ["email", "phone"],
        "storage_location": "russia",
        "integrations": [],
        "admin_access": {
            "exists": True,
            "exposed_to_internet": True,
            "mfa_enabled": False,
        },
        "has_payments": None,
        "has_electronic_signature": None,
        "has_ml_or_ai_processing": None,
        "has_logs_or_observability": True,
        "has_backups": None,
        "serves_kii_subject": None,
        "serves_government": None,
        "unknowns": [],
    }
    if overrides:
        data.update(overrides)
    return json.dumps(data)


class TestCreateLlmFn:
    def test_returns_none_when_not_configured(self) -> None:
        with patch.object(Settings, "llm_enabled", False):
            assert create_llm_fn() is None

    def test_returns_none_for_unknown_provider(self) -> None:
        with (
            patch.object(Settings, "llm_enabled", True),
            patch.object(Settings, "LLM_PROVIDER", "unknown"),
        ):
            assert create_llm_fn() is None

    def test_returns_callable_for_openrouter(self) -> None:
        with (
            patch.object(Settings, "llm_enabled", True),
            patch.object(Settings, "LLM_PROVIDER", "openrouter"),
            patch.object(Settings, "LLM_API_KEY", "sk-test"),
            patch.object(Settings, "LLM_MODEL", "qwen/qwen3.6-plus"),
        ):
            fn = create_llm_fn()
            assert fn is not None
            assert callable(fn)


class TestRunAnalysisWithLlm:
    def test_uses_heuristic_when_no_llm(self) -> None:
        result = run_analysis(
            "B2B SaaS, email registration, admin panel exposed"
        )
        assert result.architecture_profile.architecture_type is not None
        assert len(result.regulatory_triggers) >= 1

    def test_uses_llm_when_provided(self) -> None:
        mock_llm = MagicMock(return_value=_valid_llm_response())
        result = run_analysis(
            "B2B SaaS with email and phone registration",
            llm_fn=mock_llm,
        )
        assert result.architecture_profile.architecture_type == (
            ArchitectureType.b2b_saas
        )
        assert result.architecture_profile.exposure == Exposure.public_internet
        assert mock_llm.called

    def test_fallback_on_llm_error(self) -> None:
        mock_llm = MagicMock(side_effect=Exception("API error"))
        result = run_analysis(
            "B2B SaaS, email registration",
            llm_fn=mock_llm,
        )
        assert isinstance(result.architecture_profile.architecture_type, ArchitectureType)

    def test_citations_still_attached_with_llm(self) -> None:
        mock_llm = MagicMock(return_value=_valid_llm_response())
        result = run_analysis(
            "B2B SaaS, email registration",
            llm_fn=mock_llm,
        )
        assert len(result.citations) >= 1
        assert any("152" in c.document_title for c in result.citations)

    def test_full_pipeline_with_llm(self) -> None:
        mock_llm = MagicMock(return_value=_valid_llm_response({
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
                }
            ],
            "admin_access": {
                "exists": True,
                "exposed_to_internet": True,
                "mfa_enabled": False,
            },
            "has_payments": True,
            "has_electronic_signature": None,
            "has_ml_or_ai_processing": None,
            "has_logs_or_observability": True,
            "has_backups": None,
            "serves_kii_subject": None,
            "serves_government": None,
            "unknowns": [],
        }))
        result = run_analysis(
            "B2B SaaS with Sentry and payments",
            llm_fn=mock_llm,
        )
        assert result.architecture_profile.architecture_type == (
            ArchitectureType.b2b_saas
        )
        assert result.architecture_profile.has_payments is True
        assert len(result.regulatory_triggers) >= 1
        assert len(result.citations) >= 1
