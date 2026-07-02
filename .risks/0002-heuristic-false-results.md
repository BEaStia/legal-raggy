---
id: RISK-0002
category: product
status: open
likelihood: high
impact: medium
owner: project-team
review_at: 2026-07-28
last_reviewed_at: 2026-06-30
---
# Heuristics can produce false positives and negatives

## Statement
Keyword extraction and deterministic rules may miss context or infer a trigger too aggressively.

## Mitigation
Возвращать основания и clarification questions, тестировать golden cases, не скрывать uncertainty, сохранять human security/legal review flags.

## Trigger
Завершение TASK-0003, TASK-0004 и появление evaluation dataset.

## Links
[TASK-0003](../.tasks/ready-for-release/0003-heuristic-extractor.md), [TASK-0004](../.tasks/ready-for-release/0004-rule-engine.md).

## Review notes

TASK-0003 добавляет границы слов, покрытые тестами отрицания, admin-контекст для MFA, golden cases и `unknowns`. Первый review нашёл три ложных срабатывания, второй — residual case с admin и MFA клиентов в одном предложении; все замечания исправлены регрессионными тестами. Вероятность риска остаётся высокой: табличные правила не понимают произвольный контекст, поэтому стратегия mitigation не меняется.
