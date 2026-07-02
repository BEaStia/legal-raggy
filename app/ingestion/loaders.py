"""Frontmatter parser and Markdown document loader."""

import re
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from Markdown text.

    Returns (metadata_dict, body_text). If no frontmatter found, returns ({}, text).
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text.strip()

    raw_yaml = match.group(1)
    body = match.group(2).strip()

    try:
        metadata = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError:
        metadata = {}

    return metadata, body


def load_markdown_file(file_path: Path) -> tuple[dict, str]:
    """Load a Markdown file and extract frontmatter + body.

    Args:
        file_path: Path to the Markdown file.

    Returns:
        Tuple of (metadata dict, body text).

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file is not a .md file.
    """
    if file_path.suffix.lower() != ".md":
        raise ValueError(f"Expected .md file, got {file_path.suffix}")

    text = file_path.read_text(encoding="utf-8")
    return parse_frontmatter(text)


def discover_markdown_files(directory: Path) -> list[Path]:
    """Recursively find all .md files in a directory.

    Args:
        directory: Root directory to search.

    Returns:
        Sorted list of Markdown file paths.
    """
    if not directory.is_dir():
        return []
    return sorted(directory.rglob("*.md"))
