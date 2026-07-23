# Search endpoint: закрепить уже сделанную поверхность

После TASK-0019 в репозитории появился следующий шаг: `TASK-0020 (search endpoint)`. При проверке оказалось, что сам endpoint уже реализован: `POST /api/v1/search` подключён в FastAPI, принимает `query`, `mode` и `top_k`, а тесты лежат в `tests/test_search_api.py`. Не хватало другого слоя — task-файла, статьи, review и строки в traceability.

Я не стал переписывать runtime-код. Для текущего шага важнее было зафиксировать, что именно уже существует и как это проверяется. Endpoint поддерживает три режима:

1. `keyword` — ищет по локальному corpus через `KeywordRetriever`;
2. `dense` — использует Qdrant, а если он недоступен, возвращает 503;
3. `hybrid` — пытается совместить keyword и dense, но fallback'ится на keyword, если Qdrant не поднят.

Это полезная поверхность для ручной проверки RAG: можно отдельно посмотреть, какие фрагменты законов возвращаются до сборки полного compliance assessment. Такой endpoint не заменяет `/analyze`, но помогает отлаживать retrieval без LLM и без rule engine.

Проверка прошла командой `python -m pytest tests/test_search_api.py -q`: 6 тестов, включая keyword mode, hybrid fallback, dense unavailable, validation для короткого query и верхнюю границу `top_k`. Отдельно прошёл `ruff check app/api/routes/search.py tests/test_search_api.py`.

Ограничение осталось эксплуатационным: dense и полноценный hybrid зависят от доступного Qdrant и индексации corpus. Поэтому тест допускает 503 для dense mode без локального Qdrant, а hybrid сохраняет полезный результат через keyword fallback. Следующий runtime-шаг лучше делать не вокруг самого endpoint, а вокруг качества structured extraction: там уже есть LLM fallback, но нужна более строгая оценка на golden cases.
