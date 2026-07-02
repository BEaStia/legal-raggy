---
id: TASK-0018
title: Auto-update laws via cron job
status: todo
phase: implementation
priority: P1
owner: project-team
created_at: 2026-07-01
started_at: null
finished_at: null
last_activity_at: 2026-07-01
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

## Acceptance criteria
Законы обновляются автоматически раз в неделю, старые версии архивируются, лог изменений сохраняется.

## Verification
`python scripts/update_laws_cron.py`; check logs and archive.

## Review and risks
P1 для актуальности citations. Статья: `.articles/0018-auto-update-laws.md`.

## Handoff
Передать auto-update TASK-0019 (notification system).
