---
id: TASK-0003
title: Heuristic architecture extractor
status: todo
phase: implementation
priority: P0
owner: project-team
created_at: 2026-06-28
started_at: null
finished_at: null
last_activity_at: 2026-06-28
blocked: false
article: ../../.articles/0003-heuristic-extractor.md
---
# TASK-0003: Heuristic architecture extractor

## Goal
Реализовать чистую функцию `extract_architecture_profile(description)` для bootstrap-извлечения архитектурных признаков.

## Dependencies
TASK-0002; разделы 9 и 15.2 [brief](../../docs/source/initial_task.md).

## Small steps
1. Табличные тесты; 2. нормализация текста; 3. keyword rules; 4. admin access; 5. неизвестные значения.

## Acceptance criteria
Контрольный B2B SaaS определяет public exposure, email, phone, personal data, Sentry и отсутствие MFA.

## Verification
`pytest tests/test_extractor.py -v`.

## Review and risks
Проверить ложные срабатывания и детерминизм. Статья: `.articles/0003-heuristic-extractor.md`.

## Handoff
Передать профиль TASK-0004.
