"""Shared Markdown to HTML converter."""

import re


def md_to_html(md: str) -> str:
    """Convert a subset of Markdown to simple HTML.

    Supports: headings (h1-h3), unordered lists, bold key-value lines.
    """
    lines = md.split("\n")
    html_lines: list[str] = []
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
