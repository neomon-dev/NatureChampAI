"""SQLite connection and schema initialization."""

import sqlite3
from pathlib import Path
from typing import Iterator


SCHEMA = """
CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT NOT NULL,
    location_label TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    notes TEXT NOT NULL,
    photo BLOB,
    mission_completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS mission_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_title TEXT NOT NULL,
    minutes INTEGER NOT NULL,
    category TEXT NOT NULL,
    completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mission_title, completed_at)
);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


class Database:
    def __init__(self, path: Path | str) -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    def connection(self) -> sqlite3.Connection:
        return connect(self.path)
