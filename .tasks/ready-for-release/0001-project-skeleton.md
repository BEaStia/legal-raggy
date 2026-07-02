---
id: TASK-0001
title: Project skeleton and health endpoint
status: ready-for-release
phase: publication
priority: P0
owner: project-team
created_at: 2026-06-28
started_at: 2026-06-30
finished_at: 2026-06-30
last_activity_at: 2026-06-30
blocked: false
article: ../../.articles/0001-project-skeleton.md
---
# TASK-0001: Project skeleton and health endpoint

## Goal
Создать `pyproject.toml`, FastAPI `/health`, Docker Compose и README для локального запуска без внешних ключей.

## Dependencies
Нет. Следует [ADR-0002](../../.decisions/0002-deterministic-mvp-boundaries.md).

## Small steps
1. Тест `/health`; 2. минимальное приложение; 3. зависимости и Docker; 4. README; 5. smoke-test.

## Acceptance criteria
`docker compose up` поднимает API; `GET localhost:8000/health` возвращает `{"status":"ok"}`; unit-тест проходит.

## Verification
`pytest tests/test_health.py -v`; `docker compose up --build`; `Invoke-RestMethod http://localhost:8000/health`.

## Review and risks
Проверить минимальный образ, отсутствие секретов и ненужных сервисов. Статья: `.articles/0001-project-skeleton.md`.

## Handoff
После готовности начать TASK-0002.
