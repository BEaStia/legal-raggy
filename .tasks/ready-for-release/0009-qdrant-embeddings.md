---
id: TASK-0009
title: Qdrant + embeddings infrastructure
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0009-qdrant-embeddings.md
---
# TASK-0009: Qdrant + embeddings infrastructure

## Goal
Добавить Qdrant в Docker Compose, настроить эмбеддинги и индексацию корпуса.

## Dependencies
TASK-0007 (корпус готов), TASK-0008 (citations работают); раздел 19 Milestone 2 [brief](../../docs/source/initial_task.md).

## Small steps
1. Qdrant в docker-compose.yml; 2. embedding provider (e5/openai); 3. индексация chunks; 4. dense retriever; 5. интеграция в citations.

## Acceptance criteria
Qdrant поднимается через docker compose; chunks индексируются; dense search возвращает релевантные результаты.

## Verification
`pytest tests/test_dense_retrieval.py -v`; `docker compose up` с Qdrant healthy.

## Review and risks
P1 для зависимости от внешнего embedding API (fallback на e5). Статья: `.articles/0009-qdrant-embeddings.md`.

## Handoff
Qdrant добавлен в docker-compose.yml; `DenseRetriever` в `app/retrieval/dense.py`; 12 тестов в `tests/test_dense_retrieval.py`.
Embedding model: `intfloat/multilingual-e5-small` (384-dim, multilingual).
Chunk_id → UUID conversion через `uuid5` для совместимости с Qdrant.
Qdrant поднимается через docker compose с healthcheck и persistent volume.
Продолжить TASK-0010 (hybrid retrieval).
