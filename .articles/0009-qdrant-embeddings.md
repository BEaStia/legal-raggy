# Qdrant и эмбеддинги: от keyword к dense retrieval

После TASK-0007 и TASK-0008 система работает на keyword matching — это хорошо для точных совпадений, но плохо для семантических запросов. [TASK-0009](../.tasks/ready-for-release/0009-qdrant-embeddings.md) добавляет Qdrant и sentence-transformers для dense vector search.

## Как устроено

Три новых модуля:

`app/core/config.py` — Settings из environment variables: QDRANT_HOST, QDRANT_PORT, EMBEDDING_PROVIDER, EMBEDDING_MODEL. По умолчанию `intfloat/multilingual-e5-small` (384-dim, multilingual, бесплатный).

`app/core/embeddings.py` — ленивая загрузка SentenceTransformer, функции `embed_texts()` и `embed_text()`. Модель загружается один раз и переиспользуется.

`app/retrieval/qdrant_store.py` — создание коллекции, индексация chunks, поиск. Chunk_id конвертируется в UUID через `uuid5` (Qdrant требует валидные UUID). Оригинальный chunk_id сохраняется в payload для обратной совместимости.

`app/retrieval/dense.py` — `DenseRetriever` с тем же интерфейсом `search(query, top_k) → list[RetrievedChunk]`, что и `KeywordRetriever`. Это важно: dense retriever — drop-in replacement для keyword.

Docker Compose обновлён: добавлен сервис `qdrant` с healthcheck и volume для персистентности. API зависит от Qdrant через `depends_on`.

## Как проверял

`tests/test_dense_retrieval.py` — 12 тестов:

- `TestQdrantStore` — создание коллекции, индексация, поиск, empty corpus
- `TestDenseRetriever` — поиск по ПДн/ЭП/КТ, top_k limit, provenance, реальный корпус

Первый запуск упал: Qdrant требует valid UUID для point IDs, а наши chunk_id — короткие hex-строки. Исправил через `uuid5` namespace conversion.

Полный набор — 109 тестов.

## Что не сразу получилось

Изначально хотел использовать in-memory Qdrant для production, но это не работает — нужен отдельный сервис. In-memory только для тестов.

Модель `multilingual-e5-small` загружается с HuggingFace при первом вызове — это занимает ~30 секунд. В production нужно pre-warm или использовать локальный кеш.

## Что осталось

Dense retriever пока не интегрирован в основной pipeline (`run_analysis` всё ещё использует keyword). Следующий шаг — TASK-0010 (hybrid retrieval), который объединит keyword + dense scores.

Следующий шаг — TASK-0010: hybrid keyword+dense retrieval.
