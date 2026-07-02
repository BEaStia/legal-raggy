"""LangGraph workflow nodes for compliance assessment.

Each node is a pure function that reads from and writes to ComplianceState.
"""

import logging
from collections.abc import Callable
from pathlib import Path

from app.agents.state import ComplianceState
from app.models import ComplianceAssessment
from app.rules.engine import analyze_profile
from app.rules.llm_extractor import extract_with_llm
from app.services.citations import attach_citation

logger = logging.getLogger(__name__)

_DEFAULT_LAWS_DIR = Path(__file__).parent.parent.parent / "data" / "raw" / "laws"


def extract_profile_node(
    state: ComplianceState,
    llm_fn: Callable[[str, str], str] | None = None,
) -> dict:
    """Extract architecture profile from description.

    Uses LLM if available, falls back to heuristic extractor.
    """
    description = state["description"]
    try:
        profile = extract_with_llm(description, llm_fn=llm_fn)
        return {"architecture_profile": profile, "errors": []}
    except Exception as e:
        logger.error("Profile extraction failed: %s", e)
        return {
            "architecture_profile": None,
            "errors": [f"extract_profile: {e}"],
        }


def detect_triggers_node(state: ComplianceState) -> dict:
    """Run rule engine to detect triggers, flags, and controls."""
    profile = state.get("architecture_profile")
    if profile is None:
        return {"errors": ["detect_triggers: no architecture_profile"]}

    try:
        assessment = analyze_profile(profile)
        return {
            "regulatory_triggers": assessment.regulatory_triggers,
            "red_flags": assessment.red_flags,
            "recommended_controls": assessment.recommended_controls,
            "clarification_questions": assessment.clarification_questions,
            "summary": assessment.summary,
            "needs_human_security_review": assessment.needs_human_security_review,
            "needs_human_legal_review": assessment.needs_human_legal_review,
            "disclaimer": assessment.disclaimer,
            "errors": [],
        }
    except Exception as e:
        logger.error("Trigger detection failed: %s", e)
        return {"errors": [f"detect_triggers: {e}"]}


def retrieve_legal_basis_node(
    state: ComplianceState,
    laws_dir: Path | None = None,
) -> dict:
    """Retrieve legal citations for detected triggers."""
    triggers = state.get("regulatory_triggers", [])
    if not triggers:
        return {"citations": [], "errors": []}

    laws = laws_dir or _DEFAULT_LAWS_DIR
    profile = state.get("architecture_profile")
    if profile is None:
        return {"citations": [], "errors": []}

    try:
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary=state.get("summary", ""),
            regulatory_triggers=triggers,
            red_flags=state.get("red_flags", []),
            recommended_controls=state.get("recommended_controls", []),
            clarification_questions=state.get("clarification_questions", []),
            citations=[],
            needs_human_security_review=state.get(
                "needs_human_security_review", True
            ),
            needs_human_legal_review=state.get(
                "needs_human_legal_review", True
            ),
            disclaimer=state.get("disclaimer", ""),
        )
        result = attach_citation(assessment, laws)
        return {"citations": result.citations, "errors": []}
    except Exception as e:
        logger.error("Legal basis retrieval failed: %s", e)
        return {"errors": [f"retrieve_legal_basis: {e}"]}


def check_grounding_node(state: ComplianceState) -> dict:
    """Verify that triggers have supporting citations.

    Simple grounding check: at least one citation exists if triggers exist.
    """
    triggers = state.get("regulatory_triggers", [])
    citations = state.get("citations", [])

    if not triggers:
        return {"grounding_passed": True}

    grounding_ok = len(citations) > 0
    return {"grounding_passed": grounding_ok}


def finalize_node(state: ComplianceState) -> dict:
    """Assemble final ComplianceAssessment from state."""
    profile = state.get("architecture_profile")
    if profile is None:
        return {"errors": ["finalize: no architecture_profile"]}

    try:
        assessment = ComplianceAssessment(
            architecture_profile=profile,
            summary=state.get("summary", ""),
            regulatory_triggers=state.get("regulatory_triggers", []),
            red_flags=state.get("red_flags", []),
            recommended_controls=state.get("recommended_controls", []),
            clarification_questions=state.get("clarification_questions", []),
            citations=state.get("citations", []),
            needs_human_security_review=state.get(
                "needs_human_security_review", True
            ),
            needs_human_legal_review=state.get(
                "needs_human_legal_review", True
            ),
            disclaimer=state.get("disclaimer", ""),
        )
        return {"final_assessment": assessment, "errors": []}
    except Exception as e:
        logger.error("Finalization failed: %s", e)
        return {"errors": [f"finalize: {e}"]}
