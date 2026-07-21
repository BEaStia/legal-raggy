# Current state

- Updated: 2026-07-21
- Goal: Milestone 2 — Qdrant retrieval + embeddings.
- Active task: **TASK-0018 — Auto-update laws via cron job**; WIP = 1.

## Completed

- Шаг 0: second brain, Kanban, ADR, radar, risks, docs auditor, pre-commit.
- **TASK-0001–0008**: Milestone 1 — детерминированный compliance MVP (97 тестов).
- **TASK-0009**: Qdrant + embeddings infrastructure — `DenseRetriever`, sentence-transformers, docker-compose с Qdrant.
- **TASK-0010**: Hybrid retrieval — `HybridRetriever` с RRF, объединение keyword + dense scores.
- **TASK-0011**: Hybrid citations — `attach_citation()` с hybrid retrieval и fallback на keyword.
- **TASK-0012**: LLM-based extraction — `extract_with_llm()` с Pydantic validation и heuristic fallback.
- **TASK-0013**: LLM integration — `run_analysis()` с OpenRouter/Qwen3.6-plus support, env var config.
- **TASK-0014**: LangGraph workflow — `app/agents/` с state, nodes, graph. extract→detect→retrieve→grounding→finalize.
- **TASK-0015**: Grounding check + conditional routing — warning node при отсутствии citations, `add_conditional_edges`.
- **TASK-0016**: Evaluation framework — golden dataset (20 cases), precision/recall/citation coverage metrics.
- **TASK-0017**: Real laws fetcher — `scripts/fetch_laws.py` downloads 8 laws from consultant.ru with version tracking.
- **TASK-0018**: Auto-update laws via cron — in progress; structured update status, weekly cron entry, JSON logs, task article and Dockerfile script copy are implemented. Container smoke-check is still incomplete.
- **TASK-0019**: Hybrid citations in production — hybrid retrieval integrated with fallback to keyword, 6 comparison tests.
- **REVIEW-0002**: passed; замечаний нет.
- **REVIEW-0003**: passed; замечаний нет.
- **REVIEW-0004**: Milestone 2 flow review — passed with follow-up: functional RAG flow is coherent, release closure blocked by TASK-0018 container smoke-check.

## Verification

- `python -m pytest -q` — 196 passed with network access (dense/hybrid embedding model needs HuggingFace access).
- `mypy app` — passed.
- `ruff check app scripts/fetch_laws.py scripts/update_laws_cron.py tests/test_laws_update_cron.py` — passed.
- `python scripts/check_docs.py --all` — passed.
- `python -m pre_commit run --all-files` — passed.

## Constraints and blockers

- Hooks: `python3 -m pre_commit`.
- Локальная разработка: `pip install -e ".[dev]"`, затем `uvicorn app.api.main:app --reload`.
- Embedding model загружается с HuggingFace при первом вызове; full pytest can fail in sandbox without network access.
- Docker smoke-check for `laws-updater` was interrupted during heavy `torch` dependency download/install; do not mark TASK-0018 done until it completes.

## Exact next action

Finish TASK-0018 container smoke-check for `laws-updater`. If it passes, move TASK-0018 to `ready-for-release`, then create the next explicit milestone task.
