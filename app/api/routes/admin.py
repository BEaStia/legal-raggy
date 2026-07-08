"""Admin dashboard routes."""

import io
import logging
import re
from datetime import datetime
from pathlib import Path

import yaml
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from app.core.md_converter import md_to_html

logger = logging.getLogger(__name__)

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

LAWS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "raw" / "laws"
ARCHIVE_DIR = LAWS_DIR / "archive"


def _parse_frontmatter(filepath: Path) -> dict:
    """Parse frontmatter from a Markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1)) or {}
    except Exception:
        pass
    return {}


def _get_laws_info() -> list[dict]:
    """Get info about all laws in the corpus."""
    laws: list[dict] = []
    if not LAWS_DIR.exists():
        return laws

    for md_file in sorted(LAWS_DIR.glob("*.md")):
        meta = _parse_frontmatter(md_file)
        if meta:
            laws.append(
                {
                    "filename": md_file.name,
                    "title": meta.get("document_title", md_file.stem),
                    "version_date": meta.get("version_date", "Unknown"),
                    "fetched_at": meta.get("fetched_at", "Unknown"),
                    "source": meta.get("source", "local"),
                    "source_url": meta.get("source_url", "#"),
                    "checksum": meta.get("checksum", "N/A"),
                }
            )
    return laws


def _get_archive_count() -> int:
    """Count archived law versions."""
    if not ARCHIVE_DIR.exists():
        return 0
    return len(list(ARCHIVE_DIR.glob("*.md")))


def _get_last_update() -> str | None:
    """Get the most recent fetched_at date."""
    laws: list[dict] = _get_laws_info()
    dates = []
    for law in laws:
        d = law.get("fetched_at")
        if d:
            try:
                dates.append(datetime.fromisoformat(d))
            except ValueError:
                pass
    if dates:
        return max(dates).strftime("%Y-%m-%d %H:%M")
    return None


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Render the admin dashboard."""
    template = env.get_template("admin.html")
    return HTMLResponse(
        template.render(
            request=request,
            laws=_get_laws_info(),
            archive_count=_get_archive_count(),
            last_update=_get_last_update(),
            logs=[],
        )
    )


@router.get("/admin/law/{filename}", response_class=HTMLResponse)
async def view_law(request: Request, filename: str):
    """View the content of a specific law."""
    filepath = LAWS_DIR / filename
    if not filepath.exists():
        return HTMLResponse("<h1>Law not found</h1>", status_code=404)

    meta = _parse_frontmatter(filepath)
    content = filepath.read_text(encoding="utf-8")

    # Remove frontmatter from display
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    body = match.group(2) if match else content

    html_content = md_to_html(body)

    template = env.get_template("law_view.html")
    return HTMLResponse(
        template.render(
            request=request,
            title=meta.get("document_title", filename),
            version=meta.get("version_date", "Unknown"),
            html_content=html_content,
        )
    )


@router.post("/admin/refresh", response_class=HTMLResponse)
async def refresh_laws(request: Request):
    """Trigger laws refresh and redirect back to dashboard."""
    logs: list[str] = []

    handler = logging.StreamHandler(io.StringIO())
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    try:
        from scripts.fetch_laws import LAW_IDS, fetch_law

        for key in LAW_IDS:
            logs.append(f"Fetching {key}...")
            fetch_law(key, force=True)
    except Exception as e:
        logs.append(f"Error: {e}")
    finally:
        logger.removeHandler(handler)

    template = env.get_template("admin.html")
    return HTMLResponse(
        template.render(
            request=request,
            laws=_get_laws_info(),
            archive_count=_get_archive_count(),
            last_update=_get_last_update(),
            logs=logs,
        )
    )
