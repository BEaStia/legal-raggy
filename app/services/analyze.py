"""Orchestration service: description -> ComplianceAssessment."""

from pathlib import Path

from app.models import ArchitectureProfile, ComplianceAssessment
from app.rules.architecture_patterns import extract_architecture_profile
from app.rules.engine import analyze_profile
from app.services.citations import attach_citations

_DEFAULT_LAWS_DIR = Path(__file__).parent.parent.parent / "data" / "raw" / "laws"


def run_analysis(
    description: str,
    laws_dirs: list[Path] | None = None,
) -> ComplianceAssessment:
    """Extract architecture profile from description and analyze compliance.

    Args:
        description: Architecture description text.
        laws_dirs: Optional list of law corpus directories for citations.
                   Defaults to data/raw/laws relative to project root.
    """
    profile: ArchitectureProfile = extract_architecture_profile(description)
    assessment: ComplianceAssessment = analyze_profile(profile)

    dirs = laws_dirs if laws_dirs else [_DEFAULT_LAWS_DIR]
    for d in dirs:
        if d.is_dir():
            attach_citations(assessment, d)
            break

    return assessment
