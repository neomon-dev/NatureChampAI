"""CRUD operations for journal entries."""

import sqlite3
from typing import Any


class JournalRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create(self, entry: dict[str, Any]) -> int:
        cursor = self.connection.execute(
            "INSERT INTO journal_entries (entry_date, location_label, title, notes, photo, mission_completed) VALUES (?, ?, ?, ?, ?, ?)",
            (entry["entry_date"], entry.get("location_label", ""), entry["title"], entry["notes"], entry.get("photo"), int(entry.get("mission_completed", False))),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def list(self, query: str = "") -> list[sqlite3.Row]:
        term = f"%{query.strip()}%"
        return list(self.connection.execute(
            "SELECT * FROM journal_entries WHERE title LIKE ? OR notes LIKE ? OR location_label LIKE ? ORDER BY entry_date DESC, id DESC",
            (term, term, term),
        ))

    def get(self, entry_id: int) -> sqlite3.Row | None:
        return self.connection.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,)).fetchone()

    def update(self, entry_id: int, entry: dict[str, Any]) -> None:
        self.connection.execute(
            "UPDATE journal_entries SET entry_date=?, location_label=?, title=?, notes=?, photo=?, mission_completed=? WHERE id=?",
            (entry["entry_date"], entry.get("location_label", ""), entry["title"], entry["notes"], entry.get("photo"), int(entry.get("mission_completed", False)), entry_id),
        )
        self.connection.commit()

    def delete(self, entry_id: int) -> None:
        self.connection.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
        self.connection.commit()
