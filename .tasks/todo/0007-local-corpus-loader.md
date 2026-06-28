---
id: TASK-0007
title: Local Markdown corpus loader and search
status: todo
phase: implementation
priority: P1
owner: project-team
created_at: 2026-06-28
started_at: null
finished_at: null
last_activity_at: 2026-06-28
blocked: false
article: ../../.articles/0007-local-corpus-loader.md
---
# TASK-0007: Local Markdown corpus loader and search

## Goal
Загружать локальные laws/cards, делить по headings и возвращать top-k keyword matches.

## Dependencies
TASK-0001; разделы 11–13 [brief](../../docs/source/initial_task.md).

## Small steps
1. Fixture docs; 2. frontmatter parser; 3. heading chunker; 4. scoring; 5. stable top-k.

## Acceptance criteria
Chunks содержат provenance; релевантный документ находится без embeddings и сети.

## Verification
`pytest tests/test_retrieval.py -v`.

## Review and risks
Проверить path traversal, deterministic ordering и source metadata. Статья: `.articles/0007-local-corpus-loader.md`.

## Handoff
Передать retrieved chunks TASK-0008.
