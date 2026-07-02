import tempfile
import unittest
from pathlib import Path

from scripts.check_docs import audit_repository

TASK = """---
id: {id}
title: Example
status: {status}
phase: {phase}
owner: test
created_at: 2026-06-28
last_activity_at: 2026-06-28
blocked: {blocked}
unblock_action: {unblock_action}
---
# Example
"""


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for status in ("todo", "in-progress", "ready-for-release", "cancelled"):
            (self.root / ".tasks" / status).mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def write_task(
        self,
        relative: str,
        task_id: str,
        *,
        phase: str = "implementation",
        blocked: str = "false",
        unblock_action: str = "null",
    ) -> Path:
        path = self.root / relative
        path.write_text(
            TASK.format(
                id=task_id,
                status=path.parent.name,
                phase=phase,
                blocked=blocked,
                unblock_action=unblock_action,
            ),
            encoding="utf-8",
        )
        return path

    def test_rejects_more_than_one_in_progress_task(self):
        self.write_task(".tasks/in-progress/0001-a.md", "TASK-0001")
        self.write_task(".tasks/in-progress/0002-b.md", "TASK-0002")
        self.assertTrue(any("WIP limit exceeded" in e for e in audit_repository(self.root)))

    def test_rejects_duplicate_ids(self):
        self.write_task(".tasks/todo/0001-a.md", "TASK-0001")
        self.write_task(".tasks/todo/0002-b.md", "TASK-0001")
        self.assertTrue(any("duplicate id TASK-0001" in e for e in audit_repository(self.root)))

    def test_rejects_unknown_phase(self):
        self.write_task(".tasks/todo/0001-a.md", "TASK-0001", phase="telepathy")
        self.assertTrue(any("invalid phase" in e for e in audit_repository(self.root)))

    def test_rejects_blocked_task_without_unblock_action(self):
        self.write_task(".tasks/in-progress/0001-a.md", "TASK-0001", blocked="true")
        self.assertTrue(any("unblock_action" in e for e in audit_repository(self.root)))

    def test_rejects_broken_relative_link(self):
        path = self.write_task(".tasks/todo/0001-a.md", "TASK-0001")
        broken = path.read_text(encoding="utf-8") + "\n[missing](missing.md)\n"
        path.write_text(broken, encoding="utf-8")
        self.assertTrue(any("broken link" in e for e in audit_repository(self.root)))


if __name__ == "__main__":
    unittest.main()
