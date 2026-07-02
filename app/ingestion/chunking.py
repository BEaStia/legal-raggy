"""Split Markdown documents into chunks by headings."""

import hashlib
import re
from pathlib import Path

from app.ingestion.loaders import load_markdown_file
from app.models.retrieval import DocumentChunk

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def chunk_by_headings(
    file_path: Path,
    document_title: str | None = None,
    document_type: str | None = None,
) -> list[DocumentChunk]:
    """Split a Markdown file into chunks by headings.

    Each chunk corresponds to a heading section. The chunk text includes
    the heading and all content until the next heading of the same or higher level.

    Args:
        file_path: Path to the Markdown file.
        document_title: Override title from frontmatter.
        document_type: Override type from frontmatter.

    Returns:
        List of DocumentChunk objects with provenance metadata.
    """
    metadata, body = load_markdown_file(file_path)

    title = document_title or metadata.get("document_title", file_path.stem)
    doc_type = document_type or metadata.get("document_type")

    source_path = str(file_path)
    chunks: list[DocumentChunk] = []

    headings = list(HEADING_RE.finditer(body))

    if not headings:
        chunk_id = _make_chunk_id(source_path, "root")
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                document_title=title,
                document_type=doc_type,
                source_path=source_path,
                heading=None,
                text=body.strip(),
                metadata={**metadata},
            )
        )
        return chunks

    for i, match in enumerate(headings):
        heading_level = len(match.group(1))
        heading_text = match.group(2).strip()
        start = match.start()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(body)

        section_text = body[start:end].strip()
        chunk_id = _make_chunk_id(source_path, heading_text)

        chunk_metadata = {**metadata}
        chunk_metadata["heading_level"] = heading_level

        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                document_title=title,
                document_type=doc_type,
                source_path=source_path,
                heading=heading_text,
                text=section_text,
                metadata=chunk_metadata,
            )
        )

    return chunks


def load_corpus(directory: Path) -> list[DocumentChunk]:
    """Load and chunk all Markdown files in a directory tree.

    Args:
        directory: Root directory containing Markdown files.

    Returns:
        Flat list of DocumentChunk objects from all files.
    """
    from app.ingestion.loaders import discover_markdown_files

    all_chunks: list[DocumentChunk] = []
    for file_path in discover_markdown_files(directory):
        all_chunks.extend(chunk_by_headings(file_path))
    return all_chunks


def _make_chunk_id(source_path: str, heading: str) -> str:
    """Create a stable chunk ID from source path and heading."""
    raw = f"{source_path}::{heading}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
