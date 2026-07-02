from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.generation.renderer import render_assessment_markdown
from app.models import ComplianceAssessment
from app.services.analyze import run_analysis

router = APIRouter()


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1)


@router.post("/analyze", response_model=ComplianceAssessment)
def analyze(request: AnalyzeRequest) -> ComplianceAssessment:
    return run_analysis(request.description)


@router.post(
    "/analyze/markdown",
    response_class=PlainTextResponse,
    responses={200: {"content": {"text/markdown": {}}}},
)
def analyze_markdown(request: AnalyzeRequest) -> str:
    """Analyze architecture and return a Markdown report."""
    assessment = run_analysis(request.description)
    return render_assessment_markdown(assessment)
