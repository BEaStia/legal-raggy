# Первый runnable каркас

На шаге 0 я вынес в репозиторий задачи, ADR, риски и handoff — без единой строки приложения. Сначала нужна была общая память проекта, чтобы агент и человек читали одни и те же решения. Дальше по плану из [восьми задач первого этапа](../.quality/traceability.md) требовался хотя бы минимальный API: поднимается локально и в Docker, внешние ключи не нужны.

[TASK-0001](../.tasks/ready-for-release/0001-project-skeleton.md) — про эту точку: не «красивый старт», а проверяемый каркас, от которого можно наращивать модели, эвристики и правила.

## Зачем именно так

Когда проект только заводился, в репозиторий положили [исходное задание](../docs/source/initial_task.md) — подробное описание того, что в итоге должно получиться. Там, в разделе про структуру репозитория, нарисовано большое дерево: маршруты вроде `analyze.py` и `search.py`, каталог `app/core/` с конфигом, позже — Qdrant в Docker Compose.

Для первой задачи я это дерево **не** копировал целиком. Если собрать всё сразу, непонятно, почему не работает: сломан запуск или просто ещё не написана логика. Нужен был узкий критерий готовности: `docker compose up`, `GET /health`, ответ `{"status":"ok"}`.

Это же следует из [ADR-0002](../.decisions/0002-deterministic-mvp-boundaries.md): на первом этапе — детерминированная цепочка, без обязательных LLM, LangGraph и Qdrant. В compose сейчас только сервис `api`, секретов в скелете нет.

## Что появилось в репозитории

- `pyproject.toml` — FastAPI, uvicorn; для разработки: pytest, httpx, ruff;
- `app/api/main.py` и `app/api/routes/health.py` — один маршрут `GET /health`;
- `Dockerfile` на `python:3.12-slim` и `docker-compose.yml` с сервисом `api`;
- `README.md` — локальный запуск и Docker;
- `tests/test_health.py` — проверка endpoint через `TestClient`.

Остальные каталоги из исходного задания (`analyze`, `core`, retrieval и т.д.) появятся в следующих задачах — когда для них будет конкретная реализация, а не только строка в спецификации.

## Как писал тест

Сначала написал `tests/test_health.py`, потом реализацию. Тест упал с `ModuleNotFoundError` — пакета `app` ещё не было. После появления маршрута прошёл с первого прогона. Для одного health-endpoint это простая дисциплина, но она фиксирует контракт: пока тест красный, задачу не закрываем.

## Как проверял

| Команда | Результат |
|---|---|
| `pytest tests/test_health.py -v` | 1 passed |
| `python -m unittest -v` | 5 passed (док-аудитор) |
| `python scripts/check_docs.py --all` | passed |
| `docker compose up --build` + `curl localhost:8000/health` | `{"status":"ok"}` |
| `ruff check app tests` | без замечаний |

Локально ставил зависимости через `pip install -e ".[dev]"`. В Docker образ собирается из `pyproject.toml` без dev-зависимостей — для runtime этого достаточно.

## Что осталось на потом

- Pydantic-модели, эвристики, rule engine — [TASK-0002](../.tasks/ready-for-release/0002-core-models.md) и следующие задачи;
- Qdrant, `/analyze` и прочие части из [исходного задания](../docs/source/initial_task.md) — намеренно не в этой задаче.

## Следующий шаг

[TASK-0002](../.tasks/ready-for-release/0002-core-models.md): модели `ArchitectureProfile`, `ComplianceAssessment` и вложенные типы как контракт системы. Health endpoint остаётся якорем: если compose перестанет подниматься, это видно до углубления в доменную логику.
