---
id: TASK-0019
title: Hybrid citations in production pipeline
status: ready-for-release
phase: publication
priority: P0
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0019-hybrid-citations.md
---
# TASK-0019: Hybrid citations in production pipeline

## Goal
Интегрировать hybrid retriever в основной pipeline с тестами сравнения hybrid vs keyword.

## Dependencies
TASK-0010 (hybrid retriever), TASK-0017 (real laws).

## Small steps
1. Update run_analysis to use hybrid by default; 2. Add comparison test (hybrid vs keyword); 3. Add citation quality metrics; 4. Integration test with real laws.

## Acceptance criteria
run_analysis() использует hybrid retrieval при наличии Qdrant, fallback на keyword. Тесты показывают что hybrid даёт больше релевантных citations.

## Verification
`pytest tests/test_hybrid_citations_production.py -v`.

## Review and risks
P0 для качества citations. Статья: `.articles/0019-hybrid-citations.md`.

## Handoff
6 тестов в `tests/test_hybrid_citations_production.py`.
Hybrid retrieval интегрирован в production pipeline с fallback на keyword.
Тесты показывают что hybrid >= keyword по количеству citations.
Продолжить TASK-0020 (search endpoint).
