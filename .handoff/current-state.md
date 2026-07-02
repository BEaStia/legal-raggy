# Current state

- Updated: 2026-07-01
- Goal: Milestone 1 — детерминированный compliance MVP.
- Active task: **нет**; WIP = 0. Milestone 1 завершён.

## Completed

- Шаг 0: second brain, Kanban, ADR, radar, risks, docs auditor, pre-commit.
- **TASK-0001**: FastAPI skeleton, `/health`, Docker Compose, README, `tests/test_health.py`.
- **TASK-0002**: enums, `ArchitectureProfile`, `ComplianceAssessment`, вложенные модели и публичные импорты `app.models`.
- **TASK-0003**: детерминированный `extract_architecture_profile` с русскими/английскими keyword rules, отрицаниями и `unknowns`.
- **TASK-0004**: `analyze_profile()` — rule engine с triggers, red flags, controls, clarification questions.
- **TASK-0005**: `POST /analyze` — endpoint, связывающий extractor и engine через `app/services/analyze.py`.
- **TASK-0006**: `render_assessment_markdown()` — Markdown-рендерер отчёта из `ComplianceAssessment`.
- **TASK-0007**: `KeywordRetriever` — загрузка Markdown корпуса, chunking по headings, keyword search с heading boost.
- **TASK-0008**: `attach_citations()` — привязка triggers к citations из локального корпуса (152-ФЗ, 63-ФЗ, 98-ФЗ).
- **REVIEW-0002**: passed; замечаний нет.
- **REVIEW-0003**: passed; замечаний нет.

## Verification

- `pytest -v` — 97 passed.
- `mypy app` — passed.
- `ruff check app tests` — passed.
- `python scripts/check_docs.py --all` — passed.
- `docker compose up --build` — container healthy; `/health` → `{"status":"ok"}`.

## Constraints and blockers

- Hooks: `python3 -m pre_commit` (или `py -3.14 -m pre_commit` на Windows, если launcher 3.11 сломан).
- Локальная разработка: `pip install -e ".[dev]"`, затем `uvicorn app.api.main:app --reload`.

## Exact next action

Провести Milestone 1 flow review. Решить, готов ли Milestone 2 (Qdrant retrieval, embeddings).
