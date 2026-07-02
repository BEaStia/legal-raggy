---
id: TASK-0013
title: LLM integration in analysis pipeline
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0013-llm-pipeline.md
---
# TASK-0013: LLM integration in analysis pipeline

## Goal
Интегрировать LLM extractor в `run_analysis()` с конфигурацией через env vars.

## Dependencies
TASK-0012 (LLM extractor), TASK-0005 (analyze endpoint).

## Small steps
1. Update run_analysis to use extract_with_llm; 2. Add LLM_PROVIDER env var; 3. Simple OpenAI/Anthropic wrapper; 4. Tests with mock LLM; 5. API endpoint update.

## Acceptance criteria
POST /analyze использует LLM если настроен, иначе heuristic. Graceful fallback при ошибке LLM.

## Verification
`pytest tests/test_llm_pipeline.py -v`; demo с LLM.

## Review and risks
P1 для зависимости от внешнего API. Статья: `.articles/0013-llm-pipeline.md`.

## Handoff
`run_analysis()` принимает `llm_fn`; `create_llm_fn()` создаёт callable из env vars.
Поддержка OpenRouter + Qwen3.6-plus, OpenAI, Anthropic.
8 тестов в `tests/test_llm_pipeline.py`.
Milestone 3 завершён. Провести Milestone 3 flow review.
