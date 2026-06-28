---
id: TASK-0006
title: Markdown assessment renderer
status: todo
phase: implementation
priority: P1
owner: project-team
created_at: 2026-06-28
started_at: null
finished_at: null
last_activity_at: 2026-06-28
blocked: false
article: ../../.articles/0006-markdown-renderer.md
---
# TASK-0006: Markdown assessment renderer

## Goal
Реализовать `render_assessment_markdown` без обязательного LLM.

## Dependencies
TASK-0002, TASK-0004; разделы 14 и 15.4 [brief](../../docs/source/initial_task.md).

## Small steps
1. Snapshot-like tests; 2. headings; 3. structured lists; 4. citations; 5. disclaimer.

## Acceptance criteria
Отчёт содержит Summary, Profile, Triggers, Red flags, Controls, Questions, Sources и Disclaimer.

## Verification
`pytest tests/test_renderer.py -v`.

## Review and risks
Проверить escaping и обязательный disclaimer. Статья: `.articles/0006-markdown-renderer.md`.

## Handoff
Продолжить TASK-0007.
