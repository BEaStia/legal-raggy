---
id: TASK-0011
title: Hybrid citations in assessment pipeline
status: ready-for-release
phase: publication
priority: P0
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0011-hybrid-citations.md
---
# TASK-0011: Hybrid citations in assessment pipeline

## Goal
Заменить keyword-only retriever на hybrid в citation service для более релевантных citations.

## Dependencies
TASK-0008 (citations), TASK-0010 (hybrid retriever).

## Small steps
1. Update attach_citations to use HybridRetriever; 2. Qdrant initialization; 3. fallback to keyword if Qdrant unavailable; 4. integration tests.

## Acceptance criteria
run_analysis() возвращает citations из hybrid retrieval; graceful fallback при отсутствии Qdrant.

## Verification
`pytest tests/test_hybrid_citations.py -v`; полный demo с citations.

## Review and risks
P0 для качества citations. Статья: `.articles/0011-hybrid-citations.md`.

## Handoff
`attach_citation()` в `app/services/citations.py` — hybrid retrieval с fallback на keyword.
8 тестов в `tests/test_hybrid_citations.py`.
Qdrant connection с таймаутом 5s, graceful fallback при недоступности.
Milestone 2 завершён. Провести Milestone 2 flow review.
