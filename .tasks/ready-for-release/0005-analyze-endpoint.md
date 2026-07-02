---
id: TASK-0005
title: Analyze endpoint
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-06-28
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0005-analyze-endpoint.md
---
# TASK-0005: Analyze endpoint

## Goal
Добавить `POST /analyze`, связывающий extractor и rule engine через типизированные модели.

## Dependencies
TASK-0001, TASK-0003, TASK-0004; раздел 10.2 [brief](../../docs/source/initial_task.md).

## Small steps
1. API test; 2. request schema; 3. orchestration service; 4. route; 5. validation errors.

## Acceptance criteria
Endpoint принимает `description`, возвращает валидный `ComplianceAssessment` и не содержит бизнес-логики в route.

## Verification
`pytest tests/test_analyze_api.py -v`.

## Review and risks
Проверить schema и отсутствие скрытых network calls. Статья: `.articles/0005-analyze-endpoint.md`.

## Handoff
`POST /analyze` реализован; 5 API-тестов. Бизнес-логика вынесена в `app/services/analyze.py`, route содержит только схему и делегирование. Передаёт assessment TASK-0006.
