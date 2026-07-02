"""Analyze API routes."""

import re
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field

from app.generation.renderer import render_assessment_markdown
from app.models import ComplianceAssessment
from app.services.analyze import run_analysis

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1)


def _render_template(name: str, **kwargs):
    """Render a template with common context."""
    template = env.get_template(name)
    return template.render(now=datetime.now().strftime("%Y-%m-%d %H:%M"), **kwargs)


def _md_to_html(md: str) -> str:
    """Convert Markdown to simple HTML for display."""
    lines = md.split("\n")
    html_lines = []
    in_list = False
    
    for line in lines:
        if not line.strip():
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
            
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{line[2:]}</li>")
        elif line.startswith("**"):
            match = re.match(r"\*\*(.+?)\*\*: (.+)", line)
            if match:
                html_lines.append(f"<p><strong>{match.group(1)}</strong>: {match.group(2)}</p>")
            else:
                html_lines.append(f"<p>{line}</p>")
        else:
            html_lines.append(f"<p>{line}</p>")
    
    if in_list:
        html_lines.append("</ul>")
    
    return "\n".join(html_lines)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main analysis page."""
    return HTMLResponse(_render_template("index.html", request=request))


@router.post("/analyze", response_model=ComplianceAssessment)
def analyze(request: AnalyzeRequest) -> ComplianceAssessment:
    """Analyze architecture and return JSON assessment."""
    return run_analysis(request.description)


@router.post(
    "/analyze/markdown",
    response_class=PlainTextResponse,
    responses={200: {"content": {"text/markdown": {}}}},
)
def analyze_markdown(request: AnalyzeRequest) -> str:
    """Analyze architecture and return Markdown report."""
    assessment = run_analysis(request.description)
    return render_assessment_markdown(assessment)


@router.post("/analyze/html", response_class=HTMLResponse)
async def analyze_html(request: AnalyzeRequest):
    """Analyze architecture and return HTML report fragment."""
    assessment = run_analysis(request.description)
    md = render_assessment_markdown(assessment)
    html_content = _md_to_html(md)
    
    return HTMLResponse(_render_template("report.html", report_html=html_content))
