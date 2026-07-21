---
id: TASK-0018
title: Auto-update laws via cron job
status: in-progress
phase: implementation
priority: P1
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-20
finished_at: null
last_activity_at: 2026-07-20
blocked: false
article: ../../.articles/0018-auto-update-laws.md
---
# TASK-0018: Auto-update laws via cron job

## Goal
Настроить автоматическое обновление законов по расписанию (раз в неделю).

## Dependencies
TASK-0017 (fetch_laws.py script).

## Small steps
1. Create cron job script; 2. Add logging; 3. Add notification on changes; 4. Test cron execution.

## Progress
- Added `scripts/update_laws_cron.py` summary logging.
- Added weekly `crontab` entry and `laws-updater` compose profile.
- Copied `scripts/` into the Docker image so the `laws-updater` command exists at runtime.
- Changed `fetch_law()` to return structured `changed/skipped/failed` status.
- Fixed checksum comparison to use the stored frontmatter checksum.
- Added focused tests in `tests/test_laws_update_cron.py`.

## Acceptance criteria
Законы обновляются автоматически раз в неделю, старые версии архивируются, лог изменений сохраняется.

## Verification
`python -m pytest tests/test_laws_update_cron.py -q`; `python scripts/update_laws_cron.py`; check logs and archive.

## Review and risks
P1 для актуальности citations. Статья: `.articles/0018-auto-update-laws.md`.

## Handoff
Notification is currently a structured log field and warning log line, not an external delivery channel.
Передать external notification delivery отдельной задачей, если понадобится.
