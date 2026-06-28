# Technology Radar — 2026-06-28

| Ring | Item | Rationale | Review trigger |
|---|---|---|---|
| adopt | Python 3.11+ | Базовый язык из brief, типизация и зрелая экосистема | смена supported runtime |
| adopt | FastAPI + Pydantic | Типизированный HTTP API и модели | завершение TASK-0002 |
| adopt | pytest | Детерминированные тесты MVP | появление первого теста |
| adopt | Markdown docs-as-code | Единый локальный источник истины | каждая третья задача |
| trial | pre-commit docs audit | Проверяем workflow до push | после трёх задач |
| assess | Qdrant + embeddings | Кандидат Milestone 2, не нужен первому demo | завершение TASK-0008 |
| caution | LangGraph-first design | Скрывает ещё не доказанный deterministic flow | только через новый ADR |
| caution | Mandatory paid LLM | Нарушает локальный запуск без ключей | только через новый ADR |
