---
id: TASK-0015
title: Grounding check + conditional routing
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0015-grounding-routing.md
---
# TASK-0015: Grounding check + conditional routing

## Goal
Добавить conditional routing в LangGraph: если grounding failed → warning node, иначе → finalize.

## Dependencies
TASK-0014 (LangGraph workflow skeleton).

## Small steps
1. Add warning node; 2. Conditional edge from check_grounding; 3. Update state schema; 4. Tests for conditional routing.

## Acceptance criteria
Workflow маршрутизирует через warning node при отсутствии citations для triggers.

## Verification
`pytest tests/test_grounding_routing.py -v`.

## Review and risks
P1 для качества workflow. Статья: `.articles/0015-grounding-routing.md`.

## Handoff
`warning_node` + `add_conditional_edges` в graph. 5 тестов в `tests/test_grounding_routing.py`.
`errors` теперь Annotated[list[str], add_messages] для LangGraph compatibility.
Conditional routing: grounding passed → finalize, failed → warning → finalize.
Milestone 4 завершён. Провести Milestone 4 flow review.
