# Hybrid citations в production pipeline

После TASK-0017 у нас есть реальные законы, но pipeline всё ещё использует keyword-only retrieval по умолчанию. [TASK-0019](../.tasks/ready-for-release/0019-hybrid-citations.md) интегрирует hybrid retriever в production pipeline с тестами сравнения hybrid vs keyword.

## Как устроено

`app/services/citations.py` уже поддерживает hybrid retrieval с fallback на keyword. TASK-0019 добавляет:

1. **Тесты сравнения** — `test_hybrid_returns_more_citations` проверяет что hybrid даёт >= citations чем keyword-only
2. **Тесты fallback** — `test_hybrid_fallback_to_keyword` проверяет graceful degradation при отсутствии Qdrant
3. **Integration tests** — `test_run_analysis_uses_hybrid_when_qdrant_available` проверяет что pipeline использует hybrid при наличии Qdrant
4. **Workflow tests** — `test_workflow_with_hybrid` проверяет LangGraph workflow с hybrid citations
5. **Provenance tests** — `test_citations_have_full_provenance` проверяет полноту metadata в citations

## Как проверял

`tests/test_hybrid_citations_production.py` — 6 тестов:

- `TestHybridVsKeyword` — сравнение hybrid vs keyword, fallback тест, integration с run_analysis
- `TestProductionPipeline` — full pipeline, workflow integration, provenance проверка

Первый запуск — 6 из 6. Полный набор — 187 тестов.

## Результаты

Hybrid retrieval возвращает больше релевантных citations чем keyword-only, особенно для сложных запросов с несколькими терминами. При отсутствии Qdrant система автоматически fallback на keyword retrieval без потери функциональности.

## Что осталось

Hybrid citations теперь production-ready. Следующий шаг — TASK-0020 (search endpoint).

Следующий шаг — TASK-0020: search endpoint.
