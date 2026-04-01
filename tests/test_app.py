import os
import unittest
import uuid
from pathlib import Path

import app


class HelpDeskTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(__file__).resolve().parents[1] / "tmp"
        self.temp_dir.mkdir(exist_ok=True)
        self.db_path = self.temp_dir / f"test-helpdesk-{uuid.uuid4().hex}.db"
        os.environ["HELPDESK_DB"] = str(self.db_path)
        app.initialize_database()

    def tearDown(self) -> None:
        os.environ.pop("HELPDESK_DB", None)
        if self.db_path.exists():
            self.db_path.unlink()

    def test_create_issue_and_list_open_issues(self) -> None:
        issue = app.create_issue(
            title="Printer offline",
            location="Library desk",
            category="Other",
            details="The front desk printer is not responding.",
        )

        self.assertEqual(issue["status"], "open")

        issues = app.list_issues("open")
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["title"], "Printer offline")

    def test_resolve_issue_moves_issue_out_of_open_filter(self) -> None:
        issue = app.create_issue(
            title="Lab PC frozen",
            location="Engineering Lab 3",
            category="Computer Lab",
            details="One computer is stuck on the login screen.",
        )

        resolved = app.resolve_issue(issue["id"])

        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["status"], "resolved")
        self.assertEqual(app.list_issues("open"), [])
        self.assertEqual(len(app.list_issues("resolved")), 1)


if __name__ == "__main__":
    unittest.main()
