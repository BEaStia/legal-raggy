"""Tests for LangGraph compliance assessment workflow."""

import json
from pathlib import Path
from unittest.mock import MagicMock

from app.agents.graph import build_compliance_graph, run_workflow
from app.agents.nodes import (
    check_grounding_node,
    detect_triggers_node,
    extract_profile_node,
    finalize_node,
    retrieve_legal_basis_node,
)
from app.agents.state import ComplianceState
from app.models import ArchitectureProfile, ComplianceAssessment
from app.rules.engine import analyze_profile


def _valid_llm_response(overrides: dict | None = None) -> str:
    data = {
        "architecture_type": "b2b_saas",
        "exposure": "public_internet",
        "users": ["business users"],
        "data_categories": ["personal_data", "telemetry_logs"],
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


def _initial_state(description: str) -> ComplianceState:
    return {
        "description": description,
        "architecture_profile": None,
        "regulatory_triggers": [],
        "red_flags": [],
        "recommended_controls": [],
        "clarification_questions": [],
        "citations": [],
        "summary": "",
        "needs_human_security_review": True,
        "needs_human_legal_review": True,
        "disclaimer": "",
        "grounding_passed": None,
        "final_assessment": None,
        "errors": [],
    }


class TestNodes:
    def test_extract_profile_node_with_llm(self) -> None:
        mock_llm = MagicMock(return_value=_valid_llm_response())
        state = _initial_state("B2B SaaS with email")
        result = extract_profile_node(state, llm_fn=mock_llm)
        assert result["architecture_profile"] is not None
        assert result["errors"] == []

    def test_extract_profile_node_heuristic_fallback(self) -> None:
        state = _initial_state("B2B SaaS, email registration")
        result = extract_profile_node(state, llm_fn=None)
        assert result["architecture_profile"] is not None
        assert result["errors"] == []

    def test_detect_triggers_node(self) -> None:
        profile = ArchitectureProfile(
            source_description="test",
            data_categories=["personal_data"],
        )
        state: ComplianceState = {
            **_initial_state("test"),
            "architecture_profile": profile,
        }
        result = detect_triggers_node(state)
        assert len(result["regulatory_triggers"]) >= 1
        assert result["errors"] == []

    def test_detect_triggers_node_no_profile(self) -> None:
        state = _initial_state("test")
        result = detect_triggers_node(state)
        assert "detect_triggers: no architecture_profile" in result["errors"]

    def test_retrieve_legal_basis_node(self) -> None:
        laws_dir = Path(__file__).parent.parent / "data" / "raw" / "laws"
        profile = ArchitectureProfile(
            source_description="test",
            data_categories=["personal_data"],
        )
        assessment = analyze_profile(profile)
        state: ComplianceState = {
            **_initial_state("test"),
            "architecture_profile": profile,
            "regulatory_triggers": assessment.regulatory_triggers,
            "summary": assessment.summary,
            "red_flags": assessment.red_flags,
            "recommended_controls": assessment.recommended_controls,
            "clarification_questions": assessment.clarification_questions,
            "needs_human_security_review": assessment.needs_human_security_review,
            "needs_human_legal_review": assessment.needs_human_legal_review,
            "disclaimer": assessment.disclaimer,
        }
        result = retrieve_legal_basis_node(state, laws_dir=laws_dir)
        assert len(result["citations"]) >= 1
        assert result["errors"] == []

    def test_check_grounding_node_with_citations(self) -> None:
        state: ComplianceState = {
            **_initial_state("test"),
            "regulatory_triggers": [{"id": "test"}],
            "citations": [{"chunk_id": "abc"}],
        }
        result = check_grounding_node(state)
        assert result["grounding_passed"] is True

    def test_check_grounding_node_without_citations(self) -> None:
        state: ComplianceState = {
            **_initial_state("test"),
            "regulatory_triggers": [{"id": "test"}],
            "citations": [],
        }
        result = check_grounding_node(state)
        assert result["grounding_passed"] is False

    def test_finalize_node(self) -> None:
        profile = ArchitectureProfile(
            source_description="test",
            data_categories=["personal_data"],
        )
        state: ComplianceState = {
            **_initial_state("test"),
            "architecture_profile": profile,
            "summary": "test summary",
            "regulatory_triggers": [],
            "red_flags": [],
            "recommended_controls": [],
            "clarification_questions": [],
            "citations": [],
        }
        result = finalize_node(state)
        assert result["final_assessment"] is not None
        assert isinstance(result["final_assessment"], ComplianceAssessment)
        assert result["errors"] == []


class TestWorkflow:
    def test_build_graph(self) -> None:
        graph = build_compliance_graph()
        assert graph is not None

    def test_run_workflow_with_heuristic(self) -> None:
        laws_dir = Path(__file__).parent.parent / "data" / "raw" / "laws"
        result = run_workflow(
            "B2B SaaS, email registration, admin panel exposed",
            laws_dir=laws_dir,
        )
        assert result["final_assessment"] is not None
        assert result["architecture_profile"] is not None
        assert len(result["regulatory_triggers"]) >= 1
        assert len(result["citations"]) >= 1
        assert result["errors"] == []

    def test_run_workflow_with_llm(self) -> None:
        mock_llm = MagicMock(return_value=_valid_llm_response())
        laws_dir = Path(__file__).parent.parent / "data" / "raw" / "laws"
        result = run_workflow(
            "B2B SaaS with email",
            llm_fn=mock_llm,
            laws_dir=laws_dir,
        )
        assert result["final_assessment"] is not None
        assert mock_llm.called

    def test_run_workflow_errors_propagate(self) -> None:
        """Workflow should not crash even with bad input."""
        result = run_workflow("")
        assert isinstance(result["errors"], list)
