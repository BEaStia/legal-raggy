---
id: TASK-0020
title: Search endpoint release closure
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-07-21
started_at: 2026-07-21
finished_at: 2026-07-21
last_activity_at: 2026-07-21
blocked: false
article: ../../.articles/0020-search-endpoint.md
---
# TASK-0020: Search endpoint release closure

## Goal
Закрепить `POST /api/v1/search` как публичный retrieval endpoint с task-state, статьёй, traceability и review.

## Dependencies
TASK-0010 (hybrid retrieval), TASK-0019 (hybrid citations in production pipeline).

## Small steps
1. Audit existing search route; 2. verify keyword/hybrid/dense fallback behavior; 3. add task/article/review traceability; 4. update handoff.

## Acceptance criteria
Endpoint принимает `query`, `mode` (`keyword`, `dense`, `hybrid`) и `top_k`; возвращает normalized search results; валидирует короткие запросы и `top_k`; dense mode корректно сообщает о недоступном Qdrant; hybrid mode fallback'ится на keyword без падения.

## Verification
`python -m pytest tests/test_search_api.py -q`; `ruff check app/api/routes/search.py tests/test_search_api.py`; `python scripts/check_docs.py --all`.

## Review and risks
P1 для проверки retrieval вручную через API. Review: `.reviews/0005-search-endpoint.md`. Статья: `.articles/0020-search-endpoint.md`.

## Handoff
Runtime-код endpoint уже был в `app/api/routes/search.py`; задача закрывает отсутствие task/article/traceability вокруг этой фичи. Следующий шаг — выбрать новую runtime-задачу, например LLM extraction quality hardening на базе evaluation dataset.
