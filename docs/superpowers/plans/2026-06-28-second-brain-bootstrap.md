# Second Brain Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать repo-local second brain, восемь Kanban-задач из исходного brief, автоматический аудит документации и первую обучающую статью.

**Architecture:** Markdown-файлы являются источником истины, а статус задачи определяется её каталогом. Небольшой Python-скрипт без сторонних runtime-зависимостей проверяет frontmatter, ссылки, идентификаторы, WIP и Kanban-поля; `pre-commit` вызывает быстрый и полный режимы.

**Tech Stack:** Markdown, Git, Python 3.11+ standard library, unittest, pre-commit.

---

## Карта файлов

- `AGENTS.md`: обязательные правила работы агентов.
- `.tasks/**`: Definition of Workflow, шаблон и восемь task-файлов.
- `.decisions/**`: ADR-индекс, шаблон и два начальных решения.
- `.radar/**`: правила и текущая технологическая позиция.
- `.handoff/**`: формат и актуальный снимок состояния.
- `.articles/**`: правила цикла статей и статья шага 0.
- `.reviews/**`, `.risks/**`: правила и шаблоны review/risk.
- `.quality/**`: Definition of Done и матрица трассировки.
- `docs/source/initial_task.md`: неизменённый импорт входного задания.
- `scripts/check_docs.py`: проверка документационного графа и Kanban-инвариантов.
- `tests/test_check_docs.py`: unit-тесты аудитора.
- `.pre-commit-config.yaml`: вызов быстрого аудита на commit и полного на push.

### Task 1: Создать документальный каркас

**Files:** создать `AGENTS.md`, индексные документы, шаблоны и `docs/source/initial_task.md`.

- [ ] Импортировать внешний `../initial_task.md` без изменения байтов и проверить SHA-256 обеих копий.
- [ ] Создать четыре статусных каталога `.tasks/` и README с WIP=1, pull-policy, SLE и правилами переходов.
- [ ] Создать шаблоны task, ADR, review и risk с конкретными обязательными полями.
- [ ] Создать DoD, radar, handoff и правила статей.
- [ ] Проверить `git diff --check` и отсутствие пустых документов.

### Task 2: Разложить Milestone 1 и трассировку

**Files:** создать `.tasks/todo/0001-*.md` — `.tasks/todo/0008-*.md`, `.quality/traceability.md`, два ADR и начальный radar.

- [ ] Создать по одному task-файлу для Project skeleton, Core models, Heuristic extractor, Rule engine, `/analyze`, Markdown renderer, Local corpus loader и Citations.
- [ ] Для каждой задачи указать зависимости, маленькие шаги, критерии приёмки, команды проверки, review и будущую статью.
- [ ] Связать требования разделов 10–16 brief с задачами в матрице.
- [ ] Зафиксировать ADR локального second brain и границ deterministic MVP.
- [ ] Убедиться, что только `.tasks/todo/` содержит task-файлы.

### Task 3: Реализовать аудит документации через TDD

**Files:** создать `tests/test_check_docs.py`, `scripts/check_docs.py`, `.pre-commit-config.yaml`.

- [ ] Написать падающие тесты для дубликата ID, WIP>1, неизвестной фазы, блокировки без действия и сломанной относительной ссылки.

```python
class AuditTests(unittest.TestCase):
    def test_rejects_more_than_one_in_progress_task(self):
        write_task(self.root / ".tasks/in-progress/0001-a.md", "TASK-0001")
        write_task(self.root / ".tasks/in-progress/0002-b.md", "TASK-0002")
        self.assertIn("WIP limit exceeded", audit_repository(self.root))

    def test_rejects_blocked_task_without_unblock_action(self):
        task = write_task(self.root / ".tasks/in-progress/0001-a.md", "TASK-0001")
        task.write_text(task.read_text() + "\nblocked: true\n", encoding="utf-8")
        self.assertIn("unblock_action", "\n".join(audit_repository(self.root)))
```

- [ ] Запустить `python -m unittest tests.test_check_docs -v` и подтвердить ошибку импорта `scripts.check_docs`.
- [ ] Реализовать `parse_frontmatter(path)`, `markdown_links(text)`, `audit_repository(root, changed=None)` и CLI `--all`/список файлов.
- [ ] Проверять обязательные metadata, уникальность ID, WIP, phase, blocked-поля, status/path, относительные ссылки и обязательные индексные файлы.
- [ ] Повторить тесты и получить `OK`.
- [ ] Настроить local hooks:

```yaml
repos:
  - repo: local
    hooks:
      - id: docs-fast
        name: docs fast audit
        entry: python scripts/check_docs.py
        language: system
        types: [markdown]
      - id: docs-full
        name: docs full audit
        entry: python scripts/check_docs.py --all
        language: system
        pass_filenames: false
        stages: [pre-push]
```

### Task 4: Закрыть шаг 0 и выпустить статью

**Files:** создать `.articles/0000-second-brain-before-project-setup.md`, обновить `.handoff/current-state.md` и evidence в DoD.

- [ ] Написать русскоязычную статью по `.articles/STYLEGUIDE.md`: проблема, подход, Kanban, ADR/radar/handoff, review, hooks, ограничения и дальнейший цикл.
- [ ] Запустить `python scripts/check_docs.py --all`, `python -m unittest -v`, `git diff --check`.
- [ ] Проверить восемь задач командой `(Get-ChildItem .tasks/todo -File).Count` с ожидаемым результатом `8`.
- [ ] Обновить handoff точным следующим действием: начать Task 0001 и переместить только её в `in-progress`.
- [ ] Зафиксировать реализацию отдельным коммитом `docs: bootstrap project second brain`.
