---
id: TASK-0002
title: Core Pydantic models
status: ready-for-release
phase: publication
priority: P0
owner: project-team
created_at: 2026-06-28
started_at: 2026-06-30
finished_at: 2026-06-30
last_activity_at: 2026-06-30
blocked: false
article: ../../.articles/0002-core-models.md
---
# TASK-0002: Core Pydantic models

## Goal
Реализовать enums, `ArchitectureProfile`, `ComplianceAssessment` и вложенные модели из brief.

## Dependencies
TASK-0001; разделы 7 и 17 [brief](../../docs/source/initial_task.md).

## Small steps
1. Тесты валидации; 2. enums; 3. nested models; 4. assessment; 5. JSON round-trip.

## Acceptance criteria
Модели типизированы, запрещают некорректные enum-значения и сериализуют пример раздела 17.

## Verification
`pytest tests/test_models.py -v` — 12 passed; `mypy app` — passed.

## Review and risks
[REVIEW-0002](../../.reviews/0002-core-models.md) — passed, P0–P3 замечаний нет. Optional/required поля и отсутствие юридических утверждений в defaults проверены. Статья: [.articles/0002-core-models.md](../../.articles/0002-core-models.md).

## Handoff
Публичные типы из `app.models` готовы для TASK-0003 и TASK-0004.
