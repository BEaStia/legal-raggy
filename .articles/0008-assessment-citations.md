# Цитаты вместо выдумок

После TASK-0007 у системы есть корпус законов и ретривер, но отчёт по-прежнему не ссылается на источники. [TASK-0008](../.tasks/ready-for-release/0008-assessment-citations.md) закрывает этот пробел: каждый regulatory trigger получает LegalCitation из локального корпуса.

Это P0-задача. Без citations система генерирует «выдуманные» ссылки — выглядит убедительно, но не проверяемо. С citations — каждый trigger привязан к конкретному chunk из конкретного файла.

## Как устроено

`app/services/citations.py` — маппинг trigger_id → search query, поиск через `KeywordRetriever`, конвертация chunks в `LegalCitation`.

Маппинг `_TRIGGER_QUERIES` — словарь из 10 trigger-query пар. `personal_data_processing` ищет «персональные данные обработка», `electronic_signature_regulation` — «электронная подпись ЭП УКЭП», `commercial_secret_possible` — «коммерческая тайна конфиденциальность». Если trigger не в маппинге — citations для него не создаются (no-op).

`attach_citation()` принимает `ComplianceAssessment` и `laws_dir`. Если директория не существует или пуста — возвращает assessment без изменений. Это важно: система не должна падать при отсутствии корпуса.

Каждый `LegalCitation` содержит: `document_title`, `document_type`, `article` (heading из chunk), `quote` (первые 300 символов), `source` (путь к файлу), `chunk_id` (SHA-256 хеш). Это позволяет проверить любую цитату — открыть файл и найти chunk по ID.

Интеграция в `run_analysis()` — опциональный параметр `laws_dirs`. По умолчанию ищет `data/raw/laws/` относительно project root. Если передан свой список директорий — использует его. Первый найденный корпус загружается, остальные игнорируются (MVP).

## Как проверял

`tests/test_citations.py` — 10 тестов в двух классах:

- `TestAttachCitations` — unit-тесты citation service:
  - personal_data trigger → 152-ФЗ в citations
  - electronic_signature trigger → 63-ФЗ в citations
  - commercial_secret trigger → 98-ФЗ в citations
  - нет triggers = нет citations
  - все citations имеют chunk_id и source
  - missing corpus = empty citations (не crash)

- `TestRunAnalysisWithCitations` — интеграционные тесты полного pipeline:
  - B2B SaaS с email/телефоном → citations с 152-ФЗ
  - Сервис с ЭП → citations с 63-ФЗ
  - Коммерческая тайна → citations с 98-ФЗ
  - Структура assessment не ломается после добавления citations

Первый запуск — 10 из 10. Полный набор — 97 тестов.

## Что не сразу получилось

Изначально `run_analysis()` не принимал `laws_dirs` — тесты не могли подставить свой путь к корпусу. Добавил опциональный параметр с дефолтом на `data/raw/laws/`.

Первая версия `_chunk_to_citation()` создавала неиспользуемую переменную `part` — ruff поймал. Убрал.

## Что осталось

Citations сейчас привязаны к trigger через статический маппинг. В будущем можно добавить:
- Семантический поиск через Qdrant (Milestone 2)
- Динамический query generation из trigger basis
- Citation scoring и filtering по релевантности
- Версионирование законов и проверка freshness

Следующий шаг — Milestone 1 flow review и решение о готовности к Milestone 2.
