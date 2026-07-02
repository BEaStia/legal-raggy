# Локальный Kanban

Поток: `todo -> in-progress -> ready-for-release`, либо `in-progress -> cancelled`. Единица ценности — один task-файл. Начало — перенос в `in-progress`; завершение — выполненный DoD и перенос в `ready-for-release`.

WIP-лимит равен 1. Следующую задачу тянем только при свободной ёмкости: `P0/P1`, разблокировка, затем порядок зависимостей Milestone 1. Внутренняя `phase`: `implementation`, `verification`, `review`, `remediation`, `publication`.

Блокировка остаётся в `in-progress` и обязана иметь `blocked_reason`, `blocked_since`, `unblock_action`. Превышение WIP возможно только при внешнем блокере и документированном исключении.

Начальный SLE: 85% задач завершаются за 3 календарных дня. На 50% SLE проверяем размер и риски; после SLE декомпозируем или разблокируем. После каждой третьей завершённой задачи пересматриваем workflow по WIP, throughput, age и cycle time.

В `ready-for-release` задача попадает только с актуальным review SHA, статьёй по [`.articles/STYLEGUIDE.md`](../.articles/STYLEGUIDE.md), трассировкой, обновлённым handoff и пройденным `.quality/definition-of-done.md`.
