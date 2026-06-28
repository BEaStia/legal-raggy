---
id: RISK-0001
category: legal
status: open
likelihood: high
impact: high
owner: project-team
review_at: 2026-07-28
---
# Legal corpus can become stale

## Statement
Законы, подзаконные акты и официальные разъяснения меняются; локальный excerpt может перестать отражать действующую редакцию.

## Mitigation
Хранить официальный источник, дату редакции, дату получения и checksum; маркировать ответы как предварительные; требовать human legal review.

## Trigger
Добавление corpus в TASK-0007 и любое изменение citation mapping.

## Links
[TASK-0007](../.tasks/todo/0007-local-corpus-loader.md), [TASK-0008](../.tasks/todo/0008-assessment-citations.md).
