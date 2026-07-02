---
id: TASK-0010
title: Hybrid keyword + dense retrieval
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0010-hybrid-retrieval.md
---
# TASK-0010: Hybrid keyword + dense retrieval

## Goal
Объединить keyword и dense retrieval в единый hybrid retriever с нормализацией и взвешиванием scores.

## Dependencies
TASK-0007 (keyword retriever), TASK-0009 (dense retriever, Qdrant).

## Small steps
1. HybridRetriever class; 2. score normalization (min-max or rank); 3. weighted combination; 4. deduplication; 5. integration test.

## Acceptance criteria
Hybrid search возвращает более релевантные результаты, чем keyword или dense по отдельности.

## Verification
`pytest tests/test_hybrid_retrieval.py -v`.

## Review and risks
P1 для качества retrieval. Статья: `.articles/0010-hybrid-retrieval.md`.

## Handoff
`HybridRetriever` в `app/retrieval/hybrid.py`; 10 тестов в `tests/test_hybrid_retrieval.py`.
RRF с k=60, настраиваемые веса keyword/dense.
Deduplication по chunk_id, provenance сохраняется.
Продолжить TASK-0011 (hybrid citations).
