"""Fetch real Russian laws from consultant.ru and convert to Markdown.

Usage:
    python scripts/fetch_laws.py              # fetch all configured laws
    python scripts/fetch_laws.py 152-FZ       # fetch specific law
"""

import hashlib
import json
import logging
import re
import sys
from datetime import date
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

LAWS_DIR = Path(__file__).parent.parent / "data" / "raw" / "laws"
ARCHIVE_DIR = LAWS_DIR / "archive"

# Document IDs on consultant.ru
LAW_IDS = {
    "152fz_personal_data": {
        "url": "https://www.consultant.ru/document/cons_doc_LAW_61801/",
        "title": 'Федеральный закон 152-ФЗ «О персональных данных»',
        "type": "federal_law",
        "domain": "personal_data",
    },
    "149fz_information": {
        "url": "https://www.consultant.ru/document/cons_doc_LAW_160243/",
        "title": 'Федеральный закон 149-ФЗ «Об информации, информационных технологиях и о защите информации»',
        "type": "federal_law",
        "domain": "information_technology",
    },
    "63fz_electronic_signature": {
        "url": "https://www.consultant.ru/document/cons_doc_LAW_32080/",
        "title": 'Федеральный закон 63-ФЗ «Об электронной подписи»',
        "type": "federal_law",
        "domain": "electronic_signature",
    },
    "98fz_commercial_secret": {
        "url": "https://www.consultant.ru/document/cons_doc_LAW_46388/",
        "title": 'Федеральный закон 98-ФЗ «О коммерческой тайне»',
        "type": "federal_law",
        "domain": "commercial_secret",
    },
    "187fz_kii": {
        "url": "https://www.consultant.ru/document/cons_doc_LAW_236691/",
        "title": 'Федеральный закон 187-ФЗ «О безопасности критической информационной инфраструктуры Российской Федерации»',
        "type": "federal_law",
        "domain": "critical_infrastructure",
    },
    "pp1119_personal_data_security": {
        "url": "https://www.consultant.ru/document/cons_doc_LAW_92990/",
        "title": "Постановление Правительства РФ №1119 «О требованиях к защите персональных данных при их обработке в информационных системах персональных данных»",
        "type": "government_decree",
        "domain": "personal_data_security",
    },
    "fstec21_personal_data_controls": {
        "url": "https://www.consultant.ru/document/cons_doc_LAW_109492/",
        "title": "Приказ ФСТЭК России №21 «Об утверждении Состава и содержания организационных и технических мер по обеспечению безопасности персональных данных при их обработке в информационных системах персональных данных»",
        "type": "fstec_order",
        "domain": "personal_data_controls",
    },
    "fsb378_crypto_personal_data": {
        "url": "https://www.consultant.ru/document/cons_doc_LAW_86985/",
        "title": "Приказ ФСБ России №378 «Об утверждении Требований к форме квалифицированного сертификата электронной подписи»",
        "type": "fsb_order",
        "domain": "crypto_personal_data",
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


def fetch_html(url: str) -> str:
    """Fetch HTML from consultant.ru."""
    with httpx.Client(follow_redirects=True, timeout=30) as client:
        response = client.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text


def extract_version_date(html: str) -> str:
    """Extract the last revision date from the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    # Look for "последняя редакция" or date patterns
    date_pattern = re.compile(
        r"(\d{2}\.\d{2}\.\d{4}|\d{1,2}\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4})"
    )
    text = soup.get_text()
    matches = date_pattern.findall(text)
    if matches:
        return matches[-1][0]
    return str(date.today())


def extract_body_text(html: str) -> str:
    """Extract the main law text from HTML and convert to Markdown."""
    soup = BeautifulSoup(html, "html.parser")

    # Find the main content container
    content = soup.find("div", class_="content") or soup.find("body")
    if not content:
        return ""

    # Remove navigation, footer, scripts
    for tag in content.find_all(["script", "nav", "footer", "header"]):
        tag.decompose()

    # Convert HTML to Markdown
    lines: list[str] = []
    for element in content.find_all(["h1", "h2", "h3", "h4", "p", "li", "div"]):
        text = element.get_text(strip=True)
        if not text:
            continue

        tag = element.name
        if tag in ("h1", "h2", "h3", "h4"):
            level = int(tag[1])
            lines.append(f"{'#' * level} {text}")
            lines.append("")
        elif tag == "p":
            lines.append(text)
            lines.append("")
        elif tag == "li":
            lines.append(f"- {text}")
        elif tag == "div" and element.get("class"):
            classes = element.get("class", [])
            if "title" in classes or "header" in classes:
                lines.append(f"## {text}")
                lines.append("")

    return "\n".join(lines)


def compute_checksum(text: str) -> str:
    """Compute SHA-256 checksum of the text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def fetch_law(key: str, force: bool = False) -> None:
    """Fetch a single law and save as Markdown."""
    law = LAW_IDS[key]
    url = law["url"]
    filename = f"{key}.md"
    filepath = LAWS_DIR / filename

    logger.info("Fetching %s from %s", key, url)

    try:
        html = fetch_html(url)
    except Exception as e:
        logger.error("Failed to fetch %s: %s", key, e)
        return

    version_date = extract_version_date(html)
    body = extract_body_text(html)

    if not body:
        logger.warning("No body text extracted for %s", key)
        return

    checksum = compute_checksum(body)

    # Check if existing file has same checksum
    if filepath.exists() and not force:
        existing = filepath.read_text(encoding="utf-8")
        existing_checksum = compute_checksum(existing)
        if existing_checksum == checksum:
            logger.info("No changes for %s, skipping", key)
            return

    # Archive old version if exists
    if filepath.exists():
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        archive_path = ARCHIVE_DIR / f"{key}_{version_date}.md"
        filepath.rename(archive_path)
        logger.info("Archived old version to %s", archive_path.name)

    # Create new file with frontmatter
    frontmatter = (
        "---\n"
        f'document_title: "{law["title"]}"\n'
        f'document_type: "{law["type"]}"\n'
        f'domain: "{law["domain"]}"\n'
        'source: "consultant.ru"\n'
        f'source_url: "{url}"\n'
        f'version_date: "{version_date}"\n'
        f'fetched_at: "{date.today().isoformat()}"\n'
        f'checksum: "{checksum}"\n'
        "---\n\n"
    )

    filepath.write_text(frontmatter + body, encoding="utf-8")
    logger.info("Saved %s (version: %s, checksum: %s)", filename, version_date, checksum)


def main() -> None:
    """Fetch all configured laws or specific ones."""
    LAWS_DIR.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        keys = [a for a in sys.argv[1:] if a in LAW_IDS]
        if not keys:
            logger.error("Unknown law keys: %s", sys.argv[1:])
            logger.info("Available: %s", list(LAW_IDS.keys()))
            sys.exit(1)
    else:
        keys = list(LAW_IDS.keys())

    force = "--force" in sys.argv

    for key in keys:
        fetch_law(key, force=force)

    logger.info("Done. Fetched %d laws.", len(keys))


if __name__ == "__main__":
    main()
