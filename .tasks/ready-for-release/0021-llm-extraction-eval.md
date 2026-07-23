---
id: TASK-0021
title: LLM extraction evaluation support
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-07-21
started_at: 2026-07-21
finished_at: 2026-07-21
last_activity_at: 2026-07-21
blocked: false
article: ../../.articles/0021-llm-extraction-eval.md
---
# TASK-0021: LLM extraction evaluation support

## Goal
Позволить evaluation framework прогонять golden dataset не только через heuristic extractor, но и через `extract_with_llm()` с mockable `llm_fn`.

## Dependencies
TASK-0012 (LLM extractor), TASK-0016 (evaluation framework), TASK-0020 (search endpoint closure).

## Small steps
1. Add failing tests for LLM-backed evaluation; 2. add extractor injection to `evaluate_case()` and `run_evaluation()`; 3. report architecture type accuracy; 4. update docs/article/review after verification.

## Acceptance criteria
Evaluation can run with no LLM and with injected `llm_fn`; existing heuristic behavior remains default; report includes architecture type accuracy; tests do not require network or real API key.

## Verification
`python -m pytest tests/test_evaluation.py tests/test_llm_extractor.py -q`; `ruff check app/evaluation/metrics.py tests/test_evaluation.py`.

## Review and risks
P1 для качества structured extraction. Review: `.reviews/0006-llm-extraction-eval.md`. Статья: `.articles/0021-llm-extraction-eval.md`.

## Handoff
`evaluate_case()` и `run_evaluation()` принимают optional `llm_fn`; без него сохраняется heuristic behavior. Отчёт теперь включает `avg_architecture_type_accuracy`.
