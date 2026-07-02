---
id: TASK-0012
title: LLM-based structured architecture extraction
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0012-llm-extractor.md
---
# TASK-0012: LLM-based structured architecture extraction

## Goal
Заменить heuristic extractor на LLM-based structured extraction с валидацией через Pydantic schema.

## Dependencies
TASK-0003 (heuristic extractor как fallback), TASK-0002 (ArchitectureProfile schema).

## Small steps
1. LLM extractor prompt; 2. Pydantic validation; 3. fallback на heuristic; 4. tests с mock LLM; 5. integration test.

## Acceptance criteria
LLM extractor возвращает валидный ArchitectureProfile; fallback на heuristic при ошибке LLM.

## Verification
`pytest tests/test_llm_extractor.py -v`.

## Review and risks
P1 для зависимости от LLM API (fallback на heuristic). Статья: `.articles/0012-llm-extractor.md`.

## Handoff
`extract_with_llm()` в `app/rules/llm_extractor.py`; 17 тестов в `tests/test_llm_extractor.py`.
LLM extraction с Pydantic validation и heuristic fallback.
SYSTEM_PROMPT содержит все допустимые enum values.
Fallback при: отсутствие llm_fn, LLM error, invalid JSON, Pydantic validation error.
Продолжить TASK-0013 (LLM integration в pipeline).
