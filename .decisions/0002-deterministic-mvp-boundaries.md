# ADR-0002: Start with a deterministic compliance MVP

- Date: 2026-06-28
- Status: accepted

## Context

Первый полезный demo должен работать локально без API-ключей и выдавать объяснимые результаты с источниками.

## Options

Сразу использовать LLM/LangGraph/Qdrant; начать с детерминированных правил и локального keyword retrieval.

## Decision

Milestone 1 строит цепочку `description -> ArchitectureProfile -> RuleEngine -> ComplianceAssessment -> Markdown`. LLM, LangGraph, embeddings и Qdrant отложены.

## Consequences

Поведение тестируемо и воспроизводимо; качество извлечения сначала ограничено эвристиками. Расширения сохранят типизированные границы.
