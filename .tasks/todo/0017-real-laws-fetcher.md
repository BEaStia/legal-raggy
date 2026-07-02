---
id: TASK-0017
title: Fetch real laws from pravo.gov.ru
status: todo
phase: implementation
priority: P0
owner: project-team
created_at: 2026-07-01
started_at: null
finished_at: null
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0017-real-laws-fetcher.md
---
# TASK-0017: Fetch real laws from pravo.gov.ru

## Goal
Заменить MVP-заглушки реальными текстами законов с pravo.gov.ru с version tracking.

## Dependencies
TASK-0007 (corpus loader), TASK-0008 (citations).

## Small steps
1. HTML parser for pravo.gov.ru; 2. HTML→Markdown converter; 3. Version tracking metadata; 4. Auto-update script; 5. Replace MVP stubs.

## Acceptance criteria
data/raw/laws/ содержит реальные тексты 152-ФЗ, 63-ФЗ, 98-ФЗ, 187-ФЗ, 149-ФЗ с metadata (version_date, source, checksum).

## Verification
`python scripts/fetch_laws.py`; `pytest tests/test_laws_fetcher.py -v`.

## Review and risks
P0 для качества citations. pravo.gov.ru может блокировать scraping. Статья: `.articles/0017-real-laws-fetcher.md`.

## Handoff
Передать реальные тексты в pipeline TASK-0018 (auto-update).
