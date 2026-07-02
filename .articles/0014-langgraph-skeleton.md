# LangGraph workflow: от линейного pipeline к агентному

После TASK-0013 у нас есть линейный pipeline: `description → extract → analyze → citations`. Это работает, но не даёт гибкости для conditional branching, retry, grounding checks. [TASK-0014](../.tasks/ready-for-release/0014-langgraph-skeleton.md) создаёт LangGraph workflow с явными узлами и рёбрами.

## Как устроено

Три новых модуля в `app/agents/`:

`app/agents/state.py` — `ComplianceState` (TypedDict) определяет схему состояния workflow. Каждый узел читает и пишет определённые поля. State аккумулирует результаты по мере прохождения через pipeline.

`app/agents/nodes.py` — пять чистых функций-узлов:
- `extract_profile_node` — LLM или heuristic extraction
- `detect_triggers_node` — rule engine (analyze_profile)
- `retrieve_legal_basis_node` — citation retrieval из корпуса
- `check_grounding_node` — проверка: есть ли citations для triggers
- `finalize_node` — сборка финального ComplianceAssessment

Каждый узел возвращает dict с обновлениями state и списком ошибок.

`app/agents/graph.py` — `build_compliance_graph()` создаёт StateGraph:
```
START → extract_profile → detect_triggers → retrieve_legal_basis → check_grounding → finalize → END
```
`functools.partial` используется для bind параметров (llm_fn, laws_dir) к узлам.

`run_workflow()` — convenience function для invocation workflow с initial state.

## Как проверял

`tests/test_langgraph_workflow.py` — 12 тестов:

- `TestNodes` — unit-тесты каждого узла: extract с LLM, extract с heuristic, detect triggers, retrieve citations, grounding check, finalize
- `TestWorkflow` — integration тесты: build graph, run workflow с heuristic, run workflow с LLM, error propagation

Первый запуск упал: `llm_fn` не передавался в `extract_profile_node` через graph. Исправил через `functools.partial`.

Полный набор — 164 теста.

## Что не сразу получилось

Изначально импортировал `Annotated` и `add_messages` из langgraph — не использовал. Ruff поймал.

Mypy ругался на `ArchitectureProfile | None` в `retrieve_legal_basis_node`. Добавил explicit None check перед созданием ComplianceAssessment.

## Что осталось

Workflow пока линейный — нет conditional branching. Следующий шаг — TASK-0015: добавить conditional routing на основе grounding check (если grounding failed → retry или warning).

Следующий шаг — TASK-0015: grounding check + conditional routing.
