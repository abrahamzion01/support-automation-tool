import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_DB = Path(__file__).parent.parent / "data" / "support.db"


def get_connection(database_path: str | Path = DEFAULT_DB):
    return sqlite3.connect(database_path)


def initialize_database(database_path: str | Path = DEFAULT_DB):
    connection = get_connection(database_path)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request TEXT NOT NULL,
            category TEXT NOT NULL,
            confidence REAL NOT NULL,
            draft_response TEXT,
            sources TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(requests)"
        ).fetchall()
    }

    if "sources" not in columns:
        connection.execute(
            "ALTER TABLE requests ADD COLUMN sources TEXT NOT NULL DEFAULT '[]'"
        )

    connection.commit()
    connection.close()


def save_request(result, database_path: str | Path = DEFAULT_DB):
    initialize_database(database_path)

    connection = get_connection(database_path)

    cursor = connection.execute(
        """
        INSERT INTO requests (
            request,
            category,
            confidence,
            draft_response,
            sources,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result.request,
            result.classification.category,
            result.classification.confidence,
            result.draft.response,
            json.dumps(result.draft.sources),
            "pending",
            datetime.now(timezone.utc).isoformat(),
        ),
    )

    connection.commit()
    request_id = cursor.lastrowid
    connection.close()

    return request_id


def update_request(
    request_id: int,
    status: str,
    draft_response: str | None,
    database_path: str | Path = DEFAULT_DB,
):
    initialize_database(database_path)

    connection = get_connection(database_path)

    connection.execute(
        """
        UPDATE requests
        SET status = ?, draft_response = ?
        WHERE id = ?
        """,
        (
            status,
            draft_response,
            request_id,
        ),
    )

    connection.commit()
    connection.close()


def get_requests(database_path: str | Path = DEFAULT_DB):
    initialize_database(database_path)

    connection = get_connection(database_path)

    rows = connection.execute(
        """
        SELECT
            id,
            request,
            category,
            confidence,
            draft_response,
            sources,
            status,
            created_at
        FROM requests
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return rows