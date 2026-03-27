#!/usr/bin/env python3
"""
Initialize SQLite schema for the NoteMaster application.

Creates tables:
- notes
- tags
- note_tags

This script is safe to run multiple times.
"""

import os
import sqlite3
from typing import Optional


def _get_db_path() -> str:
    """
    Resolve SQLite DB path from environment.

    We rely on the shared database container convention:
    - environment variable SQLITE_DB points to the sqlite file path.
    If not set, we fall back to "myapp.db" in the current directory.
    """
    return os.environ.get("SQLITE_DB") or "myapp.db"


def _connect(db_path: str) -> sqlite3.Connection:
    """Create a sqlite connection with pragmatic defaults for API usage."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _execute(conn: sqlite3.Connection, sql: str, params: Optional[tuple] = None) -> None:
    """Execute a single SQL statement with optional params."""
    if params is None:
        conn.execute(sql)
    else:
        conn.execute(sql, params)


def main() -> None:
    """Entrypoint: initialize NoteMaster schema."""
    db_path = _get_db_path()
    print(f"[init_notes_schema] Using SQLite DB at: {db_path}")

    conn = _connect(db_path)
    try:
        _execute(
            conn,
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            )
            """,
        )
        _execute(conn, "CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at)")
        _execute(conn, "CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title)")

        _execute(
            conn,
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            )
            """,
        )
        _execute(conn, "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")

        _execute(
            conn,
            """
            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (note_id, tag_id),
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
            """,
        )
        _execute(conn, "CREATE INDEX IF NOT EXISTS idx_note_tags_note_id ON note_tags(note_id)")
        _execute(conn, "CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id ON note_tags(tag_id)")

        conn.commit()
        print("[init_notes_schema] Schema ready.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
