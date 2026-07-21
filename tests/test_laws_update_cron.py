from pathlib import Path

from scripts import fetch_laws, update_laws_cron


def test_fetch_law_skips_when_frontmatter_checksum_matches(
    tmp_path: Path,
    monkeypatch,
) -> None:
    body = "# Law\n\nCurrent text"
    checksum = fetch_laws.compute_checksum(body)
    laws_dir = tmp_path / "laws"
    archive_dir = laws_dir / "archive"
    laws_dir.mkdir()
    existing = laws_dir / "152fz_personal_data.md"
    existing.write_text(
        "\n".join(
            [
                "---",
                'document_title: "Test"',
                f'checksum: "{checksum}"',
                "---",
                "",
                body,
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(fetch_laws, "LAWS_DIR", laws_dir)
    monkeypatch.setattr(fetch_laws, "ARCHIVE_DIR", archive_dir)
    monkeypatch.setattr(fetch_laws, "fetch_html", lambda _url: "<html></html>")
    monkeypatch.setattr(fetch_laws, "extract_document_url", lambda _html: None)
    monkeypatch.setattr(fetch_laws, "extract_version_date", lambda _html: "01.01.2026")
    monkeypatch.setattr(fetch_laws, "extract_body_text", lambda _html: body)

    result = fetch_laws.fetch_law("152fz_personal_data")

    assert result["status"] == "skipped"
    assert result["changed"] is False
    assert result["checksum"] == checksum
    assert not archive_dir.exists()


def test_fetch_law_reports_change_and_archives_previous_version(
    tmp_path: Path,
    monkeypatch,
) -> None:
    laws_dir = tmp_path / "laws"
    archive_dir = laws_dir / "archive"
    laws_dir.mkdir()
    existing = laws_dir / "152fz_personal_data.md"
    existing.write_text("old text", encoding="utf-8")

    monkeypatch.setattr(fetch_laws, "LAWS_DIR", laws_dir)
    monkeypatch.setattr(fetch_laws, "ARCHIVE_DIR", archive_dir)
    monkeypatch.setattr(fetch_laws, "fetch_html", lambda _url: "<html></html>")
    monkeypatch.setattr(fetch_laws, "extract_document_url", lambda _html: None)
    monkeypatch.setattr(fetch_laws, "extract_version_date", lambda _html: "01.01.2026")
    monkeypatch.setattr(fetch_laws, "extract_body_text", lambda _html: "new text")

    result = fetch_laws.fetch_law("152fz_personal_data")

    assert result["status"] == "changed"
    assert result["changed"] is True
    assert result["archive_path"] == str(archive_dir / "152fz_personal_data_01.01.2026.md")
    assert (archive_dir / "152fz_personal_data_01.01.2026.md").read_text(
        encoding="utf-8"
    ) == "old text"
    assert "new text" in existing.read_text(encoding="utf-8")


def test_run_update_aggregates_statuses_and_notifications(monkeypatch) -> None:
    monkeypatch.setattr(
        update_laws_cron,
        "LAW_IDS",
        {
            "changed_law": {},
            "skipped_law": {},
            "failed_law": {},
        },
    )

    def fake_fetch_law(key: str, force: bool = False) -> dict:
        if key == "changed_law":
            return {
                "key": key,
                "status": "changed",
                "changed": True,
                "version_date": "01.01.2026",
            }
        if key == "skipped_law":
            return {"key": key, "status": "skipped", "changed": False}
        return {"key": key, "status": "failed", "changed": False, "error": "network"}

    monkeypatch.setattr(update_laws_cron, "fetch_law", fake_fetch_law)

    result = update_laws_cron.run_update()

    assert result["total"] == 3
    assert result["changed"] == 1
    assert result["skipped"] == 1
    assert result["failed"] == 1
    assert result["notifications"] == [
        "changed_law changed to version 01.01.2026",
        "failed_law failed: network",
    ]
