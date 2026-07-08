"""Analyze API routes."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field

from app.core.md_converter import md_to_html
from app.generation.renderer import render_assessment_markdown
from app.models import ComplianceAssessment
from app.services.analyze import run_analysis

router = APIRouter()
logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=50_000)


def _render_template(name: str, **kwargs):
    """Render a template with common context."""
    template = env.get_template(name)
    return template.render(now=datetime.now().strftime("%Y-%m-%d %H:%M"), **kwargs)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main analysis page."""
    return HTMLResponse(_render_template("index.html", request=request))


@router.post("/analyze", response_model=ComplianceAssessment)
async def analyze(request: AnalyzeRequest) -> ComplianceAssessment:
    """Analyze architecture and return JSON assessment."""
    try:
        return await asyncio.to_thread(run_analysis, request.description)
    except Exception as e:
        logger.error("Analysis failed: %s", e, exc_info=True)
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@router.post(
    "/analyze/markdown",
    response_class=PlainTextResponse,
    responses={200: {"content": {"text/markdown": {}}}},
)
async def analyze_markdown(request: AnalyzeRequest) -> str:
    """Analyze architecture and return Markdown report."""
    try:
        assessment = await asyncio.to_thread(run_analysis, request.description)
        return render_assessment_markdown(assessment)
    except Exception as e:
        logger.error("Markdown analysis failed: %s", e, exc_info=True)
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@router.post("/analyze/html", response_class=HTMLResponse)
async def analyze_html(request: AnalyzeRequest):
    """Analyze architecture and return HTML report fragment."""
    try:
        assessment = await asyncio.to_thread(run_analysis, request.description)
        md = render_assessment_markdown(assessment)
        html_content = md_to_html(md)
        return HTMLResponse(_render_template("report.html", report_html=html_content))
    except Exception as e:
        logger.error("HTML analysis failed: %s", e, exc_info=True)
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
