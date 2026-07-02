---
id: REVIEW-0003
task: TASK-0003
reviewed_commit: 353287071c5f195af15885ef55ab60b0543d7869
reviewed_state: working-tree
reviewer: independent-review-agent
status: passed
created_at: 2026-07-01
---

# Review: TASK-0003 Heuristic architecture extractor

## Scope

`app/rules/architecture_patterns.py`, `tests/test_extractor.py` и зависимости от моделей TASK-0002.

Точный проверенный снимок закреплён SHA-256 файлов:

| File | SHA-256 |
|---|---|
| `app/rules/architecture_patterns.py` | `eecc84ea0aac11175701af525ba5ab4f4fc05b0c0d5b4a18fbdc97cc9425e255` |
| `app/models/__init__.py` | `689e129c3b5c5ddc5a7f047b1524b374aca9347be4c6979c57afcd1cc9173990` |
| `app/models/architecture.py` | `26255f9363e4a52e5d98cfcebaa0b2b69f80309a8d86501447edb709fd4af665` |
| `app/models/compliance.py` | `779c4fe0093616327480f4307e48a545c7f3d4fad1b2cae41bed0e3e3a4b5bd4` |
| `tests/test_extractor.py` | `6c278818949118c3ac1df91d17daec747c5a011b7f8abc89c33cc9bf46cf47bb` |

## Automated evidence

- `pytest tests/test_extractor.py -v` — 14 passed.
- `pytest -v` — 32 passed.
- `mypy app` — no issues.
- `ruff check app tests` — passed.
- `python -m pip check` — no broken requirements.
- `python scripts/check_docs.py --all` — passed.
- Docker build/smoke — container healthy; `/health` вернул `{"status":"ok"}`.

## Findings

Открытых P0, P1, P2, P3 нет.

Два P3, выявленных при review, исправлены:

- **P3-1**: добавлен keyword «оплаты» в `_has_payments`;
- **P3-2**: добавлен тест `test_detects_mixed_storage_location`.

Проверено:

- функция чистая, детерминированная, без I/O и LLM — соответствует ADR-0002;
- NFKC-нормализация + ё→е + collapse whitespace корректно обрабатывает RU/EN текст;
- word-boundary regex `(?<!\w)...(?!\w)` не даёт ложных срабатываний на подстроках;
- отрицания (logging, public exposure, admin absence) покрыты регрессионными тестами;
- MFA корректно привязывается к admin-контексту, не к клиентскому (residual P2 из предыдущих review исправлен);
- `unknowns` список явный и actionable;
- таблица keyword rules покрывает §15.2 и §17 brief;
- `app.rules` не экспортирует приватные функции;
- интеграции с `app.models` совместимы с TASK-0002.

## Verdict

**Passed.** Критерии TASK-0003 выполнены. Замечаний нет.
