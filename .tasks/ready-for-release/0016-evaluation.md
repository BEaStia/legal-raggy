---
id: TASK-0016
title: Evaluation framework + golden dataset
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0016-evaluation.md
---
# TASK-0016: Evaluation framework + golden dataset

## Goal
Создать golden dataset (20 архитектурных описаний) и framework для измерения precision, recall, citation coverage.

## Dependencies
TASK-0008 (citations), TASK-0014 (LangGraph workflow).

## Small steps
1. Define golden dataset schema; 2. Create 20 test cases; 3. Implement metrics (precision, recall, FPR, FNR); 4. Run evaluation; 5. Report.

## Acceptance criteria
Golden dataset содержит 20 кейсов с ожидаемыми triggers/categories/flags. Metrics вычисляются автоматически.

## Verification
`pytest tests/test_evaluation.py -v`; `python scripts/run_eval.py`.

## Review and risks
P1 для качества системы. Статья: `.articles/0016-evaluation.md`.

## Handoff
`app/evaluation/` — datasets.py (20 golden cases), metrics.py (precision/recall/coverage).
`scripts/run_eval.py` — CLI evaluation script.
12 тестов в `tests/test_evaluation.py`.
Результаты: Trigger P/R 0.84/0.84, Category P/R 0.65/0.63, Citation Coverage 0.25.
Milestone 5 завершён. Провести Milestone 5 review.
