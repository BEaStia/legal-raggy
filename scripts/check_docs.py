"""Audit repository-local documentation and Kanban invariants."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


PHASES = {"implementation", "verification", "review", "remediation", "publication"}
STATUSES = {"todo", "in-progress", "ready-for-release", "cancelled"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"\'')
    return {}


def markdown_links(text: str) -> list[str]:
    return [match.group(1).split(maxsplit=1)[0].strip("<>") for match in LINK_RE.finditer(text)]


def _is_null(value: str | None) -> bool:
    return value is None or value.strip().lower() in {"", "null", "none", "~"}


def audit_repository(root: Path, changed: list[Path] | None = None) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    task_files = sorted((root / ".tasks").glob("*/*.md")) if (root / ".tasks").exists() else []
    task_files = [path for path in task_files if path.name not in {"README.md", "template.md"}]

    ids: dict[str, Path] = {}
    in_progress = 0
    required = {"id", "title", "status", "phase", "owner", "created_at", "last_activity_at", "blocked"}
    for path in task_files:
        meta = parse_frontmatter(path)
        relative = path.relative_to(root)
        missing = sorted(required - meta.keys())
        if missing:
            errors.append(f"{relative}: missing metadata {', '.join(missing)}")
        task_id = meta.get("id")
        if task_id:
            if task_id in ids:
                errors.append(f"{relative}: duplicate id {task_id} (also {ids[task_id].relative_to(root)})")
            ids[task_id] = path
        status = path.parent.name
        if status in STATUSES and meta.get("status") != status:
            errors.append(f"{relative}: status {meta.get('status')!r} does not match directory {status!r}")
        if status == "in-progress":
            in_progress += 1
        if meta.get("phase") not in PHASES:
            errors.append(f"{relative}: invalid phase {meta.get('phase')!r}")
        if meta.get("blocked", "false").lower() == "true" and _is_null(meta.get("unblock_action")):
            errors.append(f"{relative}: blocked task requires unblock_action")

    if in_progress > 1:
        errors.append(f"WIP limit exceeded: {in_progress} tasks in progress, maximum is 1")

    markdown_files = sorted(root.rglob("*.md"))
    for path in markdown_files:
        if ".git" in path.parts:
            continue
        for link in markdown_links(path.read_text(encoding="utf-8")):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_text = unquote(link.split("#", 1)[0])
            if not target_text:
                continue
            target = (path.parent / target_text).resolve()
            if not target.exists():
                errors.append(f"{path.relative_to(root)}: broken link {link}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="audit the complete repository")
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args(argv)
    errors = audit_repository(Path.cwd(), None if args.all else args.files)
    if errors:
        print("Documentation audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Documentation audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
