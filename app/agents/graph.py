"""LangGraph workflow for compliance assessment.

Pipeline:
    description
    -> extract_profile
    -> detect_triggers
    -> retrieve_legal_basis
    -> check_grounding
    -> finalize
"""

from collections.abc import Callable
from functools import partial
from pathlib import Path

from langgraph.graph import END, START, StateGraph

from app.agents.nodes import (
    check_grounding_node,
    detect_triggers_node,
    extract_profile_node,
    finalize_node,
    retrieve_legal_basis_node,
)
from app.agents.state import ComplianceState


def build_compliance_graph(
    llm_fn: Callable[[str, str], str] | None = None,
    laws_dir: Path | None = None,
):
    """Build the compliance assessment LangGraph workflow.

    Args:
        llm_fn: Optional LLM callable for architecture extraction.
        laws_dir: Optional path to laws corpus for citations.

    Returns:
        Compiled LangGraph graph ready for invocation.
    """
    workflow = StateGraph(ComplianceState)

    # Create bound node functions
    extract_node = partial(extract_profile_node, llm_fn=llm_fn)
    retrieve_node = partial(retrieve_legal_basis_node, laws_dir=laws_dir)

    # Add nodes
    workflow.add_node("extract_profile", extract_node)
    workflow.add_node("detect_triggers", detect_triggers_node)
    workflow.add_node("retrieve_legal_basis", retrieve_node)
    workflow.add_node("check_grounding", check_grounding_node)
    workflow.add_node("finalize", finalize_node)

    # Wire edges
    workflow.add_edge(START, "extract_profile")
    workflow.add_edge("extract_profile", "detect_triggers")
    workflow.add_edge("detect_triggers", "retrieve_legal_basis")
    workflow.add_edge("retrieve_legal_basis", "check_grounding")
    workflow.add_edge("check_grounding", "finalize")
    workflow.add_edge("finalize", END)

    # Bind node kwargs
    graph = workflow.compile()
    return graph


def run_workflow(
    description: str,
    llm_fn: Callable[[str, str], str] | None = None,
    laws_dir: Path | None = None,
) -> ComplianceState:
    """Run the compliance assessment workflow.

    Args:
        description: Architecture description text.
        llm_fn: Optional LLM callable for architecture extraction.
        laws_dir: Optional path to laws corpus for citations.

    Returns:
        Final ComplianceState with assessment.
    """
    graph = build_compliance_graph(llm_fn=llm_fn, laws_dir=laws_dir)

    initial_state: ComplianceState = {
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

    result = graph.invoke(initial_state)
    return result
