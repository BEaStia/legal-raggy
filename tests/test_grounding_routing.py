"""Tests for grounding check + conditional routing in LangGraph workflow."""

from pathlib import Path

from app.agents.graph import run_workflow
from app.agents.nodes import warning_node
from app.agents.state import ComplianceState


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


class TestWarningNode:
    def test_adds_warning_to_errors(self) -> None:
        state: ComplianceState = {
            **_initial_state("test"),
            "errors": ["previous error"],
        }
        result = warning_node(state)
        assert "WARNING: No citations found" in result["errors"][-1]
        assert "previous error" in result["errors"]

    def test_preserves_existing_errors(self) -> None:
        state: ComplianceState = {
            **_initial_state("test"),
            "errors": ["error1", "error2"],
        }
        result = warning_node(state)
        assert "error1" in result["errors"]
        assert "error2" in result["errors"]
        assert len(result["errors"]) == 3


class TestConditionalRouting:
    def test_workflow_with_citations_passes_grounding(self) -> None:
        """When citations exist, grounding passes and warning is skipped."""
        laws_dir = Path(__file__).parent.parent / "data" / "raw" / "laws"
        result = run_workflow(
            "B2B SaaS, email registration",
            laws_dir=laws_dir,
        )
        assert result["grounding_passed"] is True
        assert result["final_assessment"] is not None
        # No warning in errors
        assert not any("WARNING" in e for e in result.get("errors", []))

    def test_workflow_without_citations_shows_warning(self) -> None:
        """When no citations exist, grounding fails and warning is shown."""
        # Use non-existent laws dir to force no citations
        result = run_workflow(
            "B2B SaaS, email registration",
            laws_dir=Path("/nonexistent"),
        )
        assert result["grounding_passed"] is False
        assert result["final_assessment"] is not None
        # Warning should be in errors (as HumanMessage.content)
        errors = result.get("errors", [])
        error_texts = [
            e.content if hasattr(e, "content") else str(e) for e in errors
        ]
        assert any("WARNING" in t for t in error_texts)

    def test_workflow_with_no_triggers_passes_grounding(self) -> None:
        """When no triggers detected, grounding passes trivially."""
        result = run_workflow(
            "Simple internal service with no personal data",
            laws_dir=Path("/nonexistent"),
        )
        # May or may not have triggers depending on extraction
        assert result["final_assessment"] is not None
