from enum import Enum

from pydantic import BaseModel, Field

from app.models.architecture import ArchitectureProfile


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Severity(str, Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RegulatoryTrigger(BaseModel):
    id: str
    title: str
    description: str
    basis: list[str] = Field(default_factory=list)
    confidence: Confidence = Confidence.medium
    reason: str | None = None


class RedFlag(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity = Severity.medium
    reason: str | None = None


class RecommendedControl(BaseModel):
    id: str
    title: str
    description: str
    priority: Severity = Severity.medium
    related_triggers: list[str] = Field(default_factory=list)


class ClarificationQuestion(BaseModel):
    id: str
    question: str
    reason: str
    related_triggers: list[str] = Field(default_factory=list)


class LegalCitation(BaseModel):
    document_title: str
    document_type: str | None = None
    article: str | None = None
    part: str | None = None
    point: str | None = None
    quote: str | None = None
    source: str | None = None
    chunk_id: str | None = None


class ComplianceAssessment(BaseModel):
    architecture_profile: ArchitectureProfile

    summary: str
    regulatory_triggers: list[RegulatoryTrigger] = Field(default_factory=list)
    red_flags: list[RedFlag] = Field(default_factory=list)
    recommended_controls: list[RecommendedControl] = Field(default_factory=list)
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list)
    citations: list[LegalCitation] = Field(default_factory=list)

    needs_human_security_review: bool = True
    needs_human_legal_review: bool = True

    disclaimer: str
