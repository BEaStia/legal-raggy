---
id: RISK-0002
category: product
status: open
likelihood: high
impact: medium
owner: project-team
review_at: 2026-07-28
---
# Heuristics can produce false positives and negatives

## Statement
Keyword extraction and deterministic rules may miss context or infer a trigger too aggressively.

## Mitigation
Возвращать основания и clarification questions, тестировать golden cases, не скрывать uncertainty, сохранять human security/legal review flags.

## Trigger
Завершение TASK-0003, TASK-0004 и появление evaluation dataset.

## Links
[TASK-0003](../.tasks/todo/0003-heuristic-extractor.md), [TASK-0004](../.tasks/todo/0004-rule-engine.md).
