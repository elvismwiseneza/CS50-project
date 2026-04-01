"""
AI assistance note:
This file was scaffolded with the help of OpenAI Codex and then reviewed
and adjusted by the student for the final project submission.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DEFAULT_DB_PATH = BASE_DIR / "data" / "helpdesk.db"
ISSUE_ROUTE = re.compile(r"^/api/issues/(?P<issue_id>\d+)/resolve$")
VALID_STATUSES = {"all", "open", "resolved"}


def get_db_path() -> Path:
    db_override = os.environ.get("HELPDESK_DB")
    return Path(db_override) if db_override else DEFAULT_DB_PATH


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(get_connection()) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL,
                details TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'resolved')),
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def row_to_issue(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "location": row["location"],
        "category": row["category"],
        "details": row["details"],
        "status": row["status"],
        "created_at": row["created_at"],
    }


def validate_issue_payload(payload: dict[str, Any]) -> dict[str, str]:
    cleaned = {
        "title": str(payload.get("title", "")).strip(),
        "location": str(payload.get("location", "")).strip(),
        "category": str(payload.get("category", "")).strip(),
        "details": str(payload.get("details", "")).strip(),
    }

    if not all(cleaned.values()):
        raise ValueError("All fields are required.")

    for key, value in cleaned.items():
        if len(value) > 2000:
            raise ValueError(f"{key.title()} is too long.")

    return cleaned


def create_issue(title: str, location: str, category: str, details: str) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO issues (title, location, category, details, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, location, category, details, created_at),
        )
        issue_id = cursor.lastrowid
        connection.commit()

    return get_issue(issue_id)


def get_issue(issue_id: int) -> dict[str, Any] | None:
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT * FROM issues WHERE id = ?",
            (issue_id,),
        ).fetchone()
    return row_to_issue(row)


def list_issues(status: str = "all") -> list[dict[str, Any]]:
    normalized_status = status if status in VALID_STATUSES else "all"

    query = "SELECT * FROM issues"
    parameters: tuple[Any, ...] = ()
    if normalized_status != "all":
        query += " WHERE status = ?"
        parameters = (normalized_status,)

    query += " ORDER BY CASE status WHEN 'open' THEN 0 ELSE 1 END, created_at DESC"

    with closing(get_connection()) as connection:
        rows = connection.execute(query, parameters).fetchall()

    issues: list[dict[str, Any]] = []
    for row in rows:
        issue = row_to_issue(row)
        if issue is not None:
            issues.append(issue)
    return issues


def resolve_issue(issue_id: int) -> dict[str, Any] | None:
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            """
            UPDATE issues
            SET status = 'resolved'
            WHERE id = ? AND status = 'open'
            """,
            (issue_id,),
        )
        connection.commit()
        if cursor.rowcount == 0:
            row = connection.execute(
                "SELECT * FROM issues WHERE id = ?",
                (issue_id,),
            ).fetchone()
            return row_to_issue(row)

    return get_issue(issue_id)


class CampusHelpDeskHandler(BaseHTTPRequestHandler):
    server_version = "CampusHelpDesk/1.0"

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/":
            self.serve_file(TEMPLATES_DIR / "index.html", "text/html; charset=utf-8")
            return

        if parsed_url.path == "/static/styles.css":
            self.serve_file(STATIC_DIR / "styles.css", "text/css; charset=utf-8")
            return

        if parsed_url.path == "/static/app.js":
            self.serve_file(STATIC_DIR / "app.js", "application/javascript; charset=utf-8")
            return

        if parsed_url.path == "/api/issues":
            params = parse_qs(parsed_url.query)
            status = params.get("status", ["all"])[0]
            self.send_json(HTTPStatus.OK, {"issues": list_issues(status)})
            return

        self.send_error_response(HTTPStatus.NOT_FOUND, "Route not found.")

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/issues":
            self.handle_create_issue()
            return

        match = ISSUE_ROUTE.match(parsed_url.path)
        if match:
            self.handle_resolve_issue(int(match.group("issue_id")))
            return

        self.send_error_response(HTTPStatus.NOT_FOUND, "Route not found.")

    def handle_create_issue(self) -> None:
        try:
            payload = self.read_json_body()
            cleaned = validate_issue_payload(payload)
            issue = create_issue(**cleaned)
        except json.JSONDecodeError:
            self.send_error_response(HTTPStatus.BAD_REQUEST, "Request body must be valid JSON.")
            return
        except ValueError as error:
            self.send_error_response(HTTPStatus.BAD_REQUEST, str(error))
            return

        self.send_json(HTTPStatus.CREATED, {"issue": issue})

    def handle_resolve_issue(self, issue_id: int) -> None:
        issue = resolve_issue(issue_id)
        if issue is None:
            self.send_error_response(HTTPStatus.NOT_FOUND, "Issue not found.")
            return
        self.send_json(HTTPStatus.OK, {"issue": issue})

    def read_json_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)
        return json.loads(raw_body.decode("utf-8"))

    def serve_file(self, file_path: Path, content_type: str) -> None:
        if not file_path.exists():
            self.send_error_response(HTTPStatus.NOT_FOUND, "File not found.")
            return

        body = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_response(self, status: HTTPStatus, message: str) -> None:
        self.send_json(status, {"error": message})

    def log_message(self, format_string: str, *args: Any) -> None:
        return


def run_server() -> None:
    initialize_database()
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), CampusHelpDeskHandler)
    print(f"Campus Tech Help Desk Lite running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
