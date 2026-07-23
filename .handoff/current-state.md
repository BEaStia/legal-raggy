# Current state

- Updated: 2026-07-21
- Goal: Milestone 2 — Qdrant retrieval + embeddings.
- Active task: **нет**; WIP = 0.

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
- **TASK-0018**: Auto-update laws via cron — structured update status, weekly cron entry, JSON logs, `--check` smoke mode, task article and lightweight Docker `laws-updater` target are implemented.
- **TASK-0019**: Hybrid citations in production — hybrid retrieval integrated with fallback to keyword, 6 comparison tests.
- **TASK-0020**: Search endpoint release closure — `POST /api/v1/search` task/article/review/traceability are synchronized; 6 focused API tests cover keyword, hybrid fallback, dense unavailable, result shape and validation.
- **REVIEW-0002**: passed; замечаний нет.
- **REVIEW-0003**: passed; замечаний нет.
- **REVIEW-0004**: Milestone 2 flow review — passed; functional RAG flow is coherent and TASK-0018 container smoke-check passed.
- **REVIEW-0005**: Search endpoint review — passed; no P0/P1 issues.

## Verification

- `python -m pytest -q` — 196 passed with network access (dense/hybrid embedding model needs HuggingFace access).
- `mypy app` — passed.
- `ruff check app scripts/fetch_laws.py scripts/update_laws_cron.py tests/test_laws_update_cron.py` — passed.
- `python scripts/check_docs.py --all` — passed.
- `python -m pre_commit run --all-files` — passed.
- `docker build --target laws-updater -t legal-raggy-laws-updater:task-0018 .` — passed.
- `docker run --rm legal-raggy-laws-updater:task-0018 python scripts/update_laws_cron.py --check` — passed.
- `docker compose build laws-updater` — passed.
- `python -m pytest tests/test_search_api.py -q` — 6 passed.
- `ruff check app/api/routes/search.py tests/test_search_api.py` — passed.

## Constraints and blockers

- Hooks: `python3 -m pre_commit`.
- Локальная разработка: `pip install -e ".[dev]"`, затем `uvicorn app.api.main:app --reload`.
- Embedding model загружается с HuggingFace при первом вызове; full pytest can fail in sandbox without network access.
- `laws-updater` uses a lightweight Docker target; API image still includes heavy embedding dependencies.

## Exact next action

Create the next explicit runtime task. Candidate: LLM extraction quality hardening on golden cases, or external notification delivery for law update events.
