# Hybrid retrieval: keyword + dense через RRF

После TASK-0009 у системы есть два независимых ретривера — keyword и dense. Каждый хорош по-своему: keyword точен для точных совпадений, dense находит семантически близкое. [TASK-0010](../.tasks/ready-for-release/0010-hybrid-retrieval.md) объединяет их через Reciprocal Rank Fusion.

## Как устроено

`app/retrieval/hybrid.py` — `HybridRetriever` с параметрами `keyword_weight`, `dense_weight` и RRF constant `k=60`.

RRF (Reciprocal Rank Fusion) — стандартный алгоритм для объединения ранжированных списков с разными шкалами scores. Формула: `score = sum(weight / (k + rank))` для каждого retriever. При k=60 результат стабилен и не чувствителен к выбросам.

Алгоритм:
1. Оба ретривера ищут с `top_k * 3` (больше кандидатов для объединения)
2. Для каждого chunk_id считается RRF score из обоих списков
3. Результаты сортируются по убыванию RRF score
4. Возвращаются top_k уникальных chunks

`HybridRetriever` сохраняет provenance: оригинальный `DocumentChunk` из любого ретривера, `match_reason` из keyword (или "dense_similarity" если только dense).

## Как проверял

`tests/test_hybrid_retrieval.py` — 10 тестов:

- Возвращает результаты для ПДн запроса
- Top результат релевантен (152-ФЗ для "персональные данные")
- top_k limit соблюдается
- Scores убывают
- Дедупликация (одинаковые chunk_id не повторяются)
- Provenance сохраняется (source_path, heading)
- Электронная подпись → 63-ФЗ
- Коммерческая тайна → 98-ФЗ
- Кастомные веса (0.9/0.1 vs 0.1/0.9) — оба находят правильный документ
- Реальный корпус (8 законов)

Первый запуск — 10 из 10. Полный набор — 119 тестов.

## Что не сразу получилось

Изначально пытался нормализовать scores через min-max, но это нестабильно при малом количестве результатов. RRF оказался проще и надёжнее — не требует нормализации, работает с любыми score scales.

## Что осталось

Hybrid retriever пока не интегрирован в основной pipeline. Следующий шаг — TASK-0011: подключить hybrid retriever в citation service вместо keyword-only.

Следующий шаг — TASK-0011: hybrid citations.
