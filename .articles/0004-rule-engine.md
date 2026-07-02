# Правила без LLM

После TASK-0003 система умеет строить `ArchitectureProfile` из текста, но не знает, что с ним делать. [TASK-0004](../.tasks/ready-for-release/0004-rule-engine.md) закрывает этот разрыв: `analyze_profile(profile)` принимает профиль и возвращает `ComplianceAssessment` с триггерами, флагами, мерами и уточняющими вопросами.

Это продолжение [ADR-0002](../.decisions/0002-deterministic-mvp-boundaries.md) — rule engine детерминирован, не вызывает LLM и не делает категоричных юридических заявлений. Каждое следствие снабжено basis и reason, чтобы reviewer мог проверить цепочку от признака до нормы.

## Как устроено

`app/rules/engine.py` — набор чистых функций, каждая отвечает за одну область. Функции вызываются последовательно из `analyze_profile`: сначала personal data, потом public SaaS, внешние интеграции, observability, admin panel, payments, электронная подпись, коммерческая тайна и КИИ. Каждая функция добавляет свои объекты в общие списки, которые в конце собираются в `ComplianceAssessment`.

Summary собирается из подтверждённых фактов профиля, а не из догадок. Если профиль минимален, summary честно говорит, что значимых триггеров не обнаружено. Disclaimer константный — его не генерирует LLM и не меняет контекст.

## Как проверял

Сначала появился `tests/test_rule_engine.py`. Первый запуск упал на `NameError: ArchitectureType` — забыл импортировать enum после копирования imports из compliance-модуля. После исправления тесты проверяют:

- golden profile (§15.3 brief) даёт требуемые triggers, flags и controls;
- сервис без персональных данных не порождает PD-триггеров;
- admin-панель за VPN без MFA не даёт красных флагов;
- payments, electronic signature, KII — каждый со своим trigger и basis;
- внешние интеграции с `sends_personal_data=true` или `None` дают флаги, а с `false` — нет;
- все controls имеют `related_triggers`, все questions имеют reason.

16 тестов, все проходят. Отдельно `mypy app` проверяет типы, Ruff — стиль.

## Что осталось

Rule engine работает только с тем, что знает extractor. Если `extract_architecture_profile` пропустил признак, правило не сработает — это открытый [RISK-0002](../.risks/0002-heuristic-false-results.md). Позже extractor может быть заменён на LLM-структурирование, но engine останется тем же контрактом.

Следующий шаг — [TASK-0005](../.tasks/ready-for-release/0005-analyze-endpoint.md): связать extractor и engine в `POST /analyze`.
