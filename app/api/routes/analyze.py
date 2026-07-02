from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models import ComplianceAssessment
from app.services.analyze import run_analysis

router = APIRouter()


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1)


@router.post("/analyze", response_model=ComplianceAssessment)
def analyze(request: AnalyzeRequest) -> ComplianceAssessment:
    return run_analysis(request.description)
