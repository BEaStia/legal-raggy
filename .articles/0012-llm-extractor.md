# LLM extractor: от keyword rules к structured extraction

После TASK-0003 heuristic extractor работает на keyword rules — это надёжно, но ограничено. [TASK-0012](../.tasks/ready-for-release/0012-llm-extractor.md) добавляет LLM-based extraction с Pydantic validation и heuristic fallback.

## Как устроено

`app/rules/llm_extractor.py` — `extract_with_llm(description, llm_fn)`:

1. Если `llm_fn` не передан — fallback на `extract_architecture_profile` (heuristic)
2. Вызывает LLM с системным промптом, описывающим JSON schema
3. Парсит JSON из ответа (обрабатывает markdown code blocks)
4. Валидирует через `ArchitectureProfile(**data)` — Pydantic v2
5. При любой ошибке — fallback на heuristic

Системный промпт содержит все допустимые enum values для `architecture_type`, `exposure`, `data_categories`, `integration_type`. Это гарантирует, что LLM знает допустимые значения.

`_safe_coerce()` — добавляет missing `integrations` и `admin_access` пустыми списками/dict, чтобы Pydantic defaults сработали корректно.

## Как проверял

`tests/test_llm_extractor.py` — 17 тестов в трёх классах:

- `TestParseLlmResponse` — plain JSON, markdown code blocks, invalid JSON
- `TestSafeCoerce` — missing integrations, missing admin_access, preserves None
- `TestExtractWithLlm` — LLM success, fallback на None, fallback на error, fallback на invalid JSON, fallback на Pydantic validation error, parses integrations, parses admin_access, preserves source_description, markdown code blocks

Первый запуск упал: `callable | None` — `callable` это builtin функция, не тип. Исправил на `Callable[[str, str], str] | None` из `collections.abc`.

Полный набор — 144 теста.

## Что не сразу получилось

SYSTEM_PROMPT был одной длинной строкой >200 символов — ruff ругался на E501. Разбил на список enum значений и f-string конкатенацию.

## Что осталось

LLM extractor пока не интегрирован в основной pipeline (`run_analysis` всё ещё использует heuristic). Следующий шаг — TASK-0013: добавить LLM extractor в pipeline с конфигурацией через environment variables.

Следующий шаг — TASK-0013: LLM integration в pipeline.
