# Один endpoint, две функции

После TASK-0003 и TASK-0004 у системы есть extractor и rule engine, но нет точки входа, через которой их можно вызвать вместе. [TASK-0005](../.tasks/ready-for-release/0005-analyze-endpoint.md) добавляет `POST /analyze` — первый реальный API-контракт системы.

## Как устроено

Route не содержит бизнес-логики. Оркестрация вынесена в `app/services/analyze.py` — три строки: вызвать extractor, передать профиль в engine, вернуть результат. Это маленькое решение, но оно важно: если завтра extractor будет заменён на LLM или добавится кэш, route не изменится.

FastAPI валидирует вход через Pydantic-схему `AnalyzeRequest(description: str, min_length=1)` и сериализует выход через `response_model=ComplianceAssessment`. Пустая или отсутствующая description возвращает 422 — это проверяется тестами, а не догадкой.

## Как проверял

`tests/test_analyze_api.py` — пять тестов. Первый проверяет, что golden profile возвращает валидный `ComplianceAssessment` с ожидаемыми triggers и flags. Два следующих — что пустая и отсутствующая description дают 422. Четвёртый — что `source_description` в ответе совпадает с входом. Пятый — что минимальный сервис без данных возвращает пустые списки triggers, flags и controls, но `needs_human_*_review` остаётся `true`.

Все пять проходят. Полный набор — 53 теста, включая extractor, models и rule engine.

## Что осталось

Endpoint пока не поддерживает локализацию, кэш или rate limiting. Это MVP-контракт; позже можно добавить `POST /analyze/markdown` (TASK-0006) или асинхронный анализ для больших описаний.

Следующий шаг — [TASK-0006](../.tasks/ready-for-release/0006-markdown-renderer.md): Markdown-рендерер для читаемого отчёта.
