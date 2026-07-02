# Grounding check + conditional routing в LangGraph

После TASK-0014 workflow линейный — нет branching на основе результатов. [TASK-0015](../.tasks/ready-for-release/0015-grounding-routing.md) добавляет conditional routing: если grounding failed → warning node → finalize, иначе → finalize напрямую.

## Как устроено

`app/agents/nodes.py` — два новых узла:
- `check_grounding_node` — теперь возвращает routing decision через `grounding_passed`
- `warning_node` — добавляет warning в errors list без блокировки финализации

`app/agents/graph.py` — `add_conditional_edges` после `check_grounding`:
```
check_grounding → (grounding_passed?) → finalize → END
                → (grounding_failed?)  → warning → finalize → END
```

`_route_after_grounding(state)` — routing function, возвращает имя следующего узла.

`app/agents/state.py` — `errors` теперь `Annotated[list[str], add_messages]` для корректной обработки множественных обновлений от разных узлов.

## Как проверял

`tests/test_grounding_routing.py` — 5 тестов:

- `TestWarningNode` — добавляет warning к existing errors, preserves existing errors
- `TestConditionalRouting` — workflow с citations проходит grounding (warning skipped), workflow без citations показывает warning, workflow без triggers проходит grounding trivially

Первый запуск упал: LangGraph требует `Annotated` для list fields когда multiple nodes write to same key. Исправил через `add_messages` reducer.

Полный набор — 169 тестов.

## Что не сразу получилось

Изначально `errors` был просто `list[str]` — LangGraph бросал `InvalidUpdateError` когда check_grounding и warning оба писали в errors. Исправил через `Annotated[list[str], add_messages]`.

Errors теперь содержат `HumanMessage` объекты вместо строк — тесты адаптированы.

## Что осталось

Milestone 4 завершён. Следующий шаг — Milestone 4 flow review.

Следующий шаг — Milestone 4 flow review.
