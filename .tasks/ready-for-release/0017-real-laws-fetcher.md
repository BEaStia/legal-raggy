---
id: TASK-0017
title: Fetch real laws from consultant.ru
status: ready-for-release
phase: publication
priority: P0
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0017-real-laws-fetcher.md
---
# TASK-0017: Fetch real laws from consultant.ru

## Goal
Заменить MVP-заглушки реальными текстами законов с consultant.ru с version tracking.

## Handoff
`scripts/fetch_laws.py` — загрузка 8 законов с consultant.ru.
Автоматическое архивирование старых версий, version tracking, checksum.
181 тест passing с реальными текстами законов.
