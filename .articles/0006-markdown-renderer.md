# Отчёт, который можно прочитать

После TASK-0005 система принимает описание архитектуры и возвращает `ComplianceAssessment` — но в виде JSON. Человеку это неудобно: нужно парсить структуру, чтобы понять, что важно. [TASK-0006](../.tasks/ready-for-release/0006-markdown-renderer.md) добавляет `render_assessment_markdown()` — чистую функцию, которая превращает `ComplianceAssessment` в читаемый Markdown-отчёт без LLM.

## Как устроено

`app/generation/renderer.py` — набор маленьких функций, каждая рендерит одну секцию: Summary, Detected architecture profile, Regulatory triggers, Red flags, Recommended controls, Clarification questions, Sources/citations, Human review, Disclaimer. Пустые списки показывают понятное сообщение ("No regulatory triggers detected."), а не просто пустую секцию.

Human review flags (`needs_human_security_review`, `needs_human_legal_review`) вынесены в отдельную секцию — они всегда `true` по умолчанию, и это видно в отчёте. Disclaimer рендерится последним, без изменений.

## Как проверял

`tests/test_renderer.py` — 12 тестов. Первый проверяет, что минимальный assessment содержит все секции. Второй — что пустые списки показывают осмысленные сообщения. Дальше — полный assessment: triggers с basis и confidence, red flags с severity, controls с related triggers, questions с reason, citations с article/part. Отдельно проверяется, что disclaimer всегда присутствует, архитектура показывает ключевые поля, human review flags видны, и рендерер детерминирован (два вызова дают одинаковый результат).

Первый запуск упал на двух тестах: "Article 5" vs "Article: 5" (формат рендера) и отсутствующая секция human review. После добавления `_render_human_review()` и исправления теста — 12 из 12.

## Что осталось

Рендерер пока не поддерживает HTML или PDF — только Markdown. Этого достаточно для MVP; позже можно добавить шаблонизатор или LLM-генерацию на основе тех же данных.

Следующий шаг — [TASK-0007](../.tasks/ready-for-release/0007-local-corpus-loader.md): загрузка локального корпуса законов из `data/raw/laws/`.
