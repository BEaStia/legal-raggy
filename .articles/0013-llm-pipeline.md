# LLM в pipeline: OpenRouter + Qwen3.6-plus

После TASK-0012 у нас есть `extract_with_llm()`, но он не интегрирован в основной pipeline. [TASK-0013](../.tasks/ready-for-release/0013-llm-pipeline.md) добавляет LLM в `run_analysis()` с поддержкой OpenRouter и Qwen3.6-plus.

## Как устроено

`app/core/llm_provider.py` — фабрика LLM callable:
- `openrouter` — OpenAI-compatible API через `https://openrouter.ai/api/v1`
- `openai` — прямой OpenAI API
- `anthropic` — Anthropic Messages API
- fallback на `None` если провайдер не настроен

`app/core/config.py` — новые env vars:
- `LLM_PROVIDER` — "openrouter", "openai", "anthropic"
- `LLM_API_KEY` — API ключ
- `LLM_MODEL` — модель (по умолчанию `qwen/qwen3.6-plus` для OpenRouter)
- `llm_enabled` property — true если provider и key заданы

`app/services/analyze.py` — `run_analysis()` теперь принимает `llm_fn`:
- Если `llm_fn` передан — использует `extract_with_llm()`
- Если `None` — fallback на heuristic extractor
- При ошибке LLM — автоматический fallback на heuristic

## Как проверял

`tests/test_llm_pipeline.py` — 8 тестов:

- `TestCreateLlmFn` — returns None when not configured, unknown provider, returns callable for OpenRouter
- `TestRunAnalysisWithLlm` — heuristic when no LLM, LLM when provided, fallback on error, citations still attached, full pipeline with LLM

Первый запуск упал: `openai` package не установлен. Установил. Второй запуск — 8 из 8.

Полный набор — 152 теста.

## Как использовать

```bash
# OpenRouter + Qwen3.6-plus
export LLM_PROVIDER=openrouter
export LLM_API_KEY=sk-or-v1-...
export LLM_MODEL=qwen/qwen3.6-plus

# Или прямой OpenAI
export LLM_PROVIDER=openai
export LLM_API_KEY=sk-...
export LLM_MODEL=gpt-4o-mini
```

Без env vars работает heuristic extractor — никаких внешних зависимостей.

## Что не сразу получилось

Mypy ругался на Anthropic return type — сложный union из 15 block types. Исправил через `hasattr` + `type: ignore`.

## Что осталось

Milestone 3 завершён. Следующий шаг — Milestone 3 flow review с реальным LLM (нужен API key).

Следующий шаг — Milestone 3 flow review.
