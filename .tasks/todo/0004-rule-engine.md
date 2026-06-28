---
id: TASK-0004
title: Deterministic compliance rule engine
status: todo
phase: implementation
priority: P0
owner: project-team
created_at: 2026-06-28
started_at: null
finished_at: null
last_activity_at: 2026-06-28
blocked: false
article: ../../.articles/0004-rule-engine.md
---
# TASK-0004: Deterministic compliance rule engine

## Goal
Реализовать `analyze_profile(profile)` с triggers, red flags, controls и human-review flags.

## Dependencies
TASK-0002; разделы 8 и 15.3 [brief](../../docs/source/initial_task.md).

## Small steps
1. Тест правила; 2. registry правил; 3. personal data; 4. logs/admin/MFA; 5. deduplication.

## Acceptance criteria
Контрольный профиль выдаёт перечисленные в 15.3 triggers, flags и controls; каждый результат объясним.

## Verification
`pytest tests/test_rule_engine.py -v`.

## Review and risks
P1 для сильного юридического утверждения без basis. Статья: `.articles/0004-rule-engine.md`.

## Handoff
Передать pipeline TASK-0005.
