---
id: TASK-0008
title: Attach citations to assessments
status: todo
phase: implementation
priority: P0
owner: project-team
created_at: 2026-06-28
started_at: null
finished_at: null
last_activity_at: 2026-06-28
blocked: false
article: ../../.articles/0008-assessment-citations.md
---
# TASK-0008: Attach citations to assessments

## Goal
Связать triggers с локальными источниками и вернуть проверяемые citations.

## Dependencies
TASK-0004, TASK-0007; раздел 16 Task 8 [brief](../../docs/source/initial_task.md).

## Small steps
1. Failing citation tests; 2. trigger queries; 3. retrieval integration; 4. citation mapping; 5. missing-source behavior.

## Acceptance criteria
Personal data ссылается на 152-ФЗ, signature на 63-ФЗ, commercial secret на 98-ФЗ; отсутствие источника явно видно.

## Verification
`pytest tests/test_citations.py -v`; полный demo из раздела 17.

## Review and risks
P0 для выдуманной цитаты, P1 для неверной связи trigger/source. Статья: `.articles/0008-assessment-citations.md`.

## Handoff
Провести Milestone 1 flow review и решить, готов ли Milestone 2.
