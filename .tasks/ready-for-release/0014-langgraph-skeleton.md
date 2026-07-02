---
id: TASK-0014
title: LangGraph agentic workflow skeleton
status: ready-for-release
phase: publication
priority: P1
owner: project-team
created_at: 2026-07-01
started_at: 2026-07-01
finished_at: 2026-07-01
last_activity_at: 2026-07-01
blocked: false
article: ../../.articles/0014-langgraph-skeleton.md
---
# TASK-0014: LangGraph agentic workflow skeleton

## Goal
Создать LangGraph workflow с узлами: extract_profile, detect_triggers, retrieve_legal_basis, generate_assessment, check_grounding, ask_clarification_or_finalize.

## Dependencies
TASK-0005 (analyze), TASK-0008 (citations), TASK-0012 (LLM extractor).

## Small steps
1. Install langgraph; 2. Define State schema; 3. Create nodes; 4. Wire edges; 5. Test workflow execution.

## Acceptance criteria
LangGraph workflow выполняет полный pipeline от description до ComplianceAssessment.

## Verification
`pytest tests/test_langgraph_workflow.py -v`.

## Review and risks
P1 для новой зависимости (langgraph). Статья: `.articles/0014-langgraph-skeleton.md`.

## Handoff
`app/agents/` — state, nodes, graph. 12 тестов в `tests/test_langgraph_workflow.py`.
LangGraph workflow: extract_profile → detect_triggers → retrieve_legal_basis → check_grounding → finalize.
`functools.partial` для bind параметров к узлам.
Продолжить TASK-0015 (grounding check + conditional routing).
