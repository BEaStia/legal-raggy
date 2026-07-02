# Правила работы с проектом

Перед изменениями прочитайте `.handoff/current-state.md`, активную задачу, связанные ADR и риски (каталоги создаются по мере необходимости).

## Workflow

1. WIP равен одной задаче. Task-файл перемещается между `.tasks/todo`, `in-progress`, `ready-for-release`, `cancelled`; копии запрещены.
2. Работайте малыми изменениями. Посторонний рефакторинг оформляйте новой задачей.
3. Следуйте TDD для поведения: тест должен упасть до реализации и пройти после неё.
4. До готовности выполните `.quality/definition-of-done.md`, полный аудит и независимое review текущего SHA.
5. `P0/P1` исправляются; `P2` исправляется либо принимается через риск/ADR; `P3` можно вернуть в backlog.
6. Значимое решение получает ADR. Изменение принятого решения создаёт новый ADR и supersedes-ссылку.
7. Обновляйте radar при смене технологической позиции, risk register при изменении риска и handoff после рабочего сеанса.
8. Каждая завершённая задача рождает русскоязычную статью по `.articles/STYLEGUIDE.md`: инженерный дневник с фактами, проверками и ограничениями; без выдуманных команд и юридической уверенности.
9. Юридические выводы всегда предварительные, снабжены источниками и требуют человеческой юридической проверки.
10. Не используйте `--no-verify` без записанной причины; CI обязан повторить полный локальный аудит.

## Команды

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install --hook-type pre-commit --hook-type pre-push

# Verify (run in this order)
ruff check . && ruff format --check .
mypy .
pytest -v

# Dev server
uvicorn app.api.main:app --reload --port 8000

# Docker
docker compose up --build

# Docs audit (also runs via pre-commit/pre-push)
python scripts/check_docs.py          # changed files only
python scripts/check_docs.py --all    # full repo
```

## Архитектура

- **Точка входа**: `app.api.main:app` (FastAPI). Роуты в `app/api/routes/`.
- **Rule engine**: `app.rules.architecture_patterns.extract_architecture_profile()` — детерминированный парсинг свободного текста (RU/EN), без LLM.
- **Модели**: Pydantic v2 в `app/models/`. `ComplianceAssessment` требует `summary` и `disclaimer` — без дефолтов.
- **Тесты**: pytest, `testpaths = ["tests"]`. Никаких фикстур или внешних сервисов не требуется.
- **Lint**: ruff (`E`, `F`, `I`, `UP`), line-length 100, target py312.
