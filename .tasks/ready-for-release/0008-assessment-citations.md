---
id: TASK-0008
title: Attach citations to assessments
status: ready-for-release
phase: publication
priority: P0
owner: project-team
created_at: 2026-06-28
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
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
`attach_citations()` реализован в `app/services/citations.py`; 10 тестов в `tests/test_citations.py`.
`run_analysis()` теперь принимает `laws_dirs` и автоматически добавляет citations.
Personal data → 152-ФЗ, signature → 63-ФЗ, commercial secret → 98-ФЗ.
Отсутствие источника = пустой citations list; missing corpus = graceful no-op.
Milestone 1 завершён. Провести Milestone 1 flow review и решить, готов ли Milestone 2.
