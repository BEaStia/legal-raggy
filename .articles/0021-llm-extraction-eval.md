# LLM extraction в evaluation: проверять без реального API

В TASK-0012 LLM extractor уже умел возвращать `ArchitectureProfile` и fallback'иться на heuristic extractor. Но evaluation framework из TASK-0016 по-прежнему проверял только heuristic path. Это создавало слепую зону: можно было менять prompt или provider wrapper, но golden dataset не давал способа сравнить structured extraction без живого API.

В TASK-0021 я добавил в `evaluate_case()` и `run_evaluation()` optional `llm_fn`. Если он не передан, всё работает как раньше через `extract_architecture_profile()`. Если передан, evaluation вызывает `extract_with_llm()` и прогоняет тот же golden case через Pydantic validation и fallback-механику LLM extractor.

Заодно добавлена метрика `avg_architecture_type_accuracy`. Поле `expected_architecture_type` уже было в `GoldenCase`, но раньше не участвовало в отчёте. Теперь evaluation отдельно показывает, насколько extractor попадает в тип архитектуры, а trigger/category precision и recall остаются на своих местах.

Проверка намеренно не требует сетевого доступа и API key. В тестах используется mock `llm_fn`, который строит JSON по golden case. Это не измеряет качество конкретной модели, зато проверяет contract: prompts доходят до LLM callable, JSON проходит через `extract_with_llm()`, результат сравнивается с golden expectations, а heuristic default не ломается.

Команда `python -m pytest tests/test_evaluation.py tests/test_llm_extractor.py -q` прошла: 31 тест. `ruff check app/evaluation/metrics.py tests/test_evaluation.py` тоже прошёл.

Ограничение важное: mock LLM не доказывает качество реального OpenRouter/OpenAI provider. Следующий шаг — отдельный eval-runner, который сможет запускать небольшой набор golden cases с настоящим provider при наличии ключа и сохранять JSON-отчёт без юридических выводов.
