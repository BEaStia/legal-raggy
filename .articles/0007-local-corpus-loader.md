# Корпус без сети и эмбеддингов

После TASK-0006 система умеет принимать описание архитектуры, извлекать факты, находить триггеры и рендерить Markdown-отчёт. Но отчёт пустой в части citations — некуда ссылаться. [TASK-0007](../.tasks/ready-for-release/0007-local-corpus-loader.md) заполняет этот пробел: загружает локальные Markdown-файлы законов и архитектурных карточек, делит их по заголовкам и возвращает top-k совпадений по ключевым словам. Без Qdrant, без эмбеддингов, без внешних API.

## Как устроено

Три слоя: парсер frontmatter, чанкер по заголовкам, ключевой ретривер.

`app/ingestion/loaders.py` — извлекает YAML-метаданные из Markdown через регулярку `^---\s*\n(.*?)\n---\s*\n(.*)`. Если frontmatter нет или YAML битый — возвращает пустой dict и тело документа. `discover_markdown_files` рекурсивно находит все `.md` в директории.

`app/ingestion/chunking.py` — делит документ по заголовкам `# Heading`. Каждый чанк — один heading section с полным текстом от заголовка до следующего. chunk_id — SHA-256 хеш от `source_path::heading`, стабильный между запусками. Каждый `DocumentChunk` хранит provenance: `document_title`, `document_type`, `source_path`, `heading`, `metadata` из frontmatter.

`app/retrieval/keyword.py` — `KeywordRetriever` токенизирует запрос и текст чанка, фильтрует стоп-слова (русские и английские), считает TF с бустом за совпадение в заголовке. Результаты сортируются по score descending, при равном score — по chunk_id для детерминизма. `match_reason` показывает, какие токены совпали.

## Корпус

`data/raw/laws/` — 8 файлов: 152-ФЗ, 149-ФЗ, 63-ФЗ, 98-ФЗ, 187-ФЗ, ПП РФ №1119, ФСТЭК №21, ФСБ №378. Каждый с frontmatter (`document_title`, `document_type`, `domain`, `source`, `version_note`).

`data/raw/architecture_cards/` — 12 карточек: b2b_saas, public_website, public_saas, internal_service, integration_api, observability_stack, hybrid_public_private, ml_ai_pipeline, payment_service, edo_signature_service, kii_client_service, support_backoffice. Каждая описывает типичные данные, триггеры, red flags и recommended controls.

## Как проверял

`tests/test_retrieval.py` — 22 теста в шести классах:

- `TestParseFrontmatter` — парсит YAML, обрабатывает отсутствие frontmatter и битый YAML
- `TestLoadMarkdownFile` — загружает файл, ругается на не-.md
- `TestDiscoverMarkdownFiles` — рекурсивный поиск, пустая директория
- `TestChunkByHeadings` — делит по заголовкам, provenance, стабильные chunk_id
- `TestLoadCorpus` — загрузка всех файлов
- `TestKeywordRetriever` — находит релевантные чанки для ПДн, ЭП, КТ; пустой результат для несуществующего запроса; top_k limit; scores и match_reason; descending order; heading boost; загрузка реального корпуса; детерминизм

Первый запуск прошёл без ошибок — 22 из 22. Полный набор — 87 тестов.

## Что не сразу получилось

Изначально хотел использовать BM25 через внешнюю библиотеку, но решил не добавлять зависимость ради MVP. Простой TF с heading boost работает достаточно хорошо для коротких юридических текстов.

Стоп-слова пришлось собрать вручную — русские и английские. Список не идеальный, но покрывает основные служебные слова.

## Что осталось

Ретривер пока работает только с keyword matching. В Milestone 2 добавится Qdrant с эмбеддингами для семантического поиска. Но для TASK-0008 (citations) keyword-поиска достаточно: триггеры имеют чёткие ключевые слова («персональные данные» → 152-ФЗ, «электронная подпись» → 63-ФЗ).

Следующий шаг — [TASK-0008](../.tasks/ready-for-release/0008-assessment-citations.md): связать триггеры с retrieved citations.
