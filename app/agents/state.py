"""LangGraph workflow state for compliance assessment."""

from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from app.models import (
    ArchitectureProfile,
    ClarificationQuestion,
    ComplianceAssessment,
    LegalCitation,
    RecommendedControl,
    RedFlag,
    RegulatoryTrigger,
)


class ComplianceState(TypedDict):
    """State for the compliance assessment workflow.

    Each node updates specific fields. The workflow accumulates
    results as it progresses through the pipeline.
    """

    # Input
    description: str

    # Node outputs (accumulated)
    architecture_profile: ArchitectureProfile | None
    regulatory_triggers: list[RegulatoryTrigger]
    red_flags: list[RedFlag]
    recommended_controls: list[RecommendedControl]
    clarification_questions: list[ClarificationQuestion]
    citations: list[LegalCitation]
    summary: str

    # Metadata
    needs_human_security_review: bool
    needs_human_legal_review: bool
    disclaimer: str

    # Workflow metadata
    grounding_passed: bool | None
    final_assessment: ComplianceAssessment | None
    errors: Annotated[list[str], add_messages]
