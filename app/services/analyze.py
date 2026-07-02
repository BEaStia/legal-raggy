"""Orchestration service: description -> ComplianceAssessment."""

from collections.abc import Callable
from pathlib import Path

from app.models import ArchitectureProfile, ComplianceAssessment
from app.rules.engine import analyze_profile
from app.rules.llm_extractor import extract_with_llm
from app.services.citations import attach_citation

_DEFAULT_LAWS_DIR = (
    Path(__file__).parent.parent.parent / "data" / "raw" / "laws"
)


def run_analysis(
    description: str,
    laws_dirs: list[Path] | None = None,
    llm_fn: Callable[[str, str], str] | None = None,
) -> ComplianceAssessment:
    """Extract architecture profile from description and analyze compliance.

    Args:
        description: Architecture description text.
        laws_dirs: Optional list of law corpus directories for citations.
                   Defaults to data/raw/laws relative to project root.
        llm_fn: Optional LLM callable for structured extraction.
                If None, uses heuristic extractor.
    """
    profile: ArchitectureProfile = extract_with_llm(
        description, llm_fn=llm_fn
    )
    assessment: ComplianceAssessment = analyze_profile(profile)

    dirs = laws_dirs if laws_dirs else [_DEFAULT_LAWS_DIR]
    for d in dirs:
        if d.is_dir():
            attach_citation(assessment, d)
            break

    return assessment
