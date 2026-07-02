# Current state

- Updated: 2026-07-01
- Goal: Milestone 2 — Qdrant retrieval + embeddings.
- Active task: **нет**; WIP = 0.

## Completed

- Шаг 0: second brain, Kanban, ADR, radar, risks, docs auditor, pre-commit.
- **TASK-0001–0008**: Milestone 1 — детерминированный compliance MVP (97 тестов).
- **TASK-0009**: Qdrant + embeddings infrastructure — `DenseRetriever`, sentence-transformers, docker-compose с Qdrant.
- **REVIEW-0002**: passed; замечаний нет.
- **REVIEW-0003**: passed; замечаний нет.

## Verification

- `pytest -v` — 109 passed.
- `mypy app` — passed.
- `ruff check app tests` — passed.
- `python scripts/check_docs.py --all` — passed.

## Constraints and blockers

- Hooks: `python3 -m pre_commit`.
- Локальная разработка: `pip install -e ".[dev]"`, затем `uvicorn app.api.main:app --reload`.
- Embedding model загружается с HuggingFace при первом вызове (~30s).

## Exact next action

Начать **TASK-0010** (hybrid retrieval) — объединить keyword + dense scores.
