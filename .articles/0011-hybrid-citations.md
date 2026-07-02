# Hybrid citations: от keyword к hybrid retrieval

После TASK-0010 у системы есть `HybridRetriever`, но citation service всё ещё использует keyword-only. [TASK-0011](../.tasks/ready-for-release/0011-hybrid-citations.md) переключает citations на hybrid retrieval с graceful fallback.

## Как устроено

`app/services/citations.py` — полностью переписан. Теперь `attach_citation()` (единственное число, переименовано для консистентности) пытается использовать hybrid retrieval, а при отсутствии Qdrant падает на keyword-only.

Алгоритм:
1. Создаётся `KeywordRetriever` из `laws_dir`
2. Если `use_hybrid=True`, пробуем подключиться к Qdrant
3. Если Qdrant доступен — загружаем chunks, создаём коллекцию, индексируем, создаём `HybridRetriever`
4. Если Qdrant недоступен — fallback на `KeywordRetriever`
5. Для каждого trigger ищем через retriever, создаём `LegalCitation`

`_try_create_qdrant_client()` — пытается подключиться к Qdrant с таймаутом 5 секунд. Если не удалось — возвращает `None`, и система работает без Qdrant.

`_attach_with_retriever()` — общая функция для любого retriever с интерфейсом `search(query, top_k)`. Это позволяет легко добавить новые retriever в будущем.

## Как проверял

`tests/test_hybrid_citations.py` — 8 тестов:

- PD trigger → 152-ФЗ
- Signature trigger → 63-ФЗ
- Commercial secret → 98-ФЗ
- Нет triggers = нет citations
- Missing corpus = нет citations
- Citations имеют provenance (chunk_id, source, quote)
- Force keyword fallback (`use_hybrid=False`) работает
- Multiple triggers → multiple citations из разных законов

Полный набор — 127 тестов.

## Что не сразу получилось

Изначально функция называлась `attach_citations` (множественное число), но это не соответствует стилю остальных функций (`analyze_profile`, `run_analysis`). Переименовал в `attach_citation`.

Qdrant warning в тестах — нормально, это in-memory клиент без сервера.

## Что осталось

Milestone 2 завершён. Следующий шаг — Milestone 2 flow review и решение о готовности к Milestone 3 (LLM structured extraction).

Следующий шаг — Milestone 2 flow review.
