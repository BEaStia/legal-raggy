# Evaluation framework: golden dataset + metrics

После TASK-0015 у нас есть полный workflow, но нет способа измерить качество. [TASK-0016](../.tasks/ready-for-release/0016-evaluation.md) создаёт golden dataset из 20 кейсов и framework для измерения precision, recall, citation coverage.

## Как устроено

`app/evaluation/datasets.py` — `GOLDEN_DATASET` из 20 `GoldenCase`:
- case_01: B2B SaaS с ПДн
- case_02: Public website с analytics
- case_03: Internal service с commercial secret
- case_04: Payment service
- case_05: EDO с УКЭП
- case_06: ML pipeline с ПДн
- case_07: Integration API с CRM
- case_08: KII subject (банк)
- case_09: Observability stack
- case_10: Hybrid architecture
- case_11: Minimal service
- case_12: Mobile backend
- case_13: DWH/BI
- case_14: Public SaaS с MFA
- case_15: Government service
- case_16: EDO без подписи
- case_17: Payment с ПДн
- case_18: ML без ПДн
- case_19: Integration с observability
- case_20: Complex B2B SaaS (платежи + ЭДО + CRM)

`app/evaluation/metrics.py` — `evaluate_case()` и `run_evaluation()`:
- Trigger precision/recall: сравнение detected vs expected triggers
- Category precision/recall: сравнение detected vs expected data categories
- Citation coverage: fraction of triggers with at least one citation
- False positives/negatives: списки для каждого кейса

`scripts/run_eval.py` — CLI script для запуска evaluation и печати отчёта.

## Результаты

```
Trigger Precision:     0.838
Trigger Recall:        0.838
Category Precision:    0.650
Category Recall:       0.625
Citation Coverage:     0.250
Total False Positives: 5
Total False Negatives: 7
```

Trigger precision/recall ~84% — неплохо для heuristic extractor.
Category precision/recall ~63% — хуже, т.к. extractor не всегда детектирует все категории.
Citation coverage 25% — низкая, т.к. citations тестируются без Qdrant (keyword-only).

## Как проверял

`tests/test_evaluation.py` — 12 тестов:
- Precision/recall: perfect match, partial, no overlap, empty cases
- Golden dataset: 20 cases, all have IDs and descriptions
- Evaluate case: evaluates specific cases correctly
- Run evaluation: returns aggregate metrics for all 20 cases

Полный набор — 181 тест.

## Что осталось

Milestone 5 завершён. Следующий шаг — Milestone 5 review.

Следующий шаг — Milestone 5 review.
