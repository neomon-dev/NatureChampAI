"""Progress and achievement queries."""

import sqlite3


class ProgressRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def record_mission(self, title: str, minutes: int, category: str) -> None:
        existing = self.connection.execute(
            "SELECT 1 FROM mission_completions WHERE mission_title = ? AND date(completed_at) = date('now')",
            (title,),
        ).fetchone()
        if existing:
            return
        self.connection.execute(
            "INSERT INTO mission_completions (mission_title, minutes, category) VALUES (?, ?, ?)",
            (title, minutes, category),
        )
        self.connection.commit()

    def summary(self) -> dict[str, int]:
        row = self.connection.execute(
            "SELECT COUNT(*) AS missions, COALESCE(SUM(minutes), 0) AS minutes, COUNT(DISTINCT category) AS categories FROM mission_completions"
        ).fetchone()
        entries = self.connection.execute("SELECT COUNT(*) FROM journal_entries").fetchone()[0]
        return {"missions": row["missions"], "minutes": row["minutes"], "categories": row["categories"], "entries": entries}

    def weekly_minutes(self) -> list[tuple[str, int]]:
        rows = self.connection.execute(
            "SELECT date(completed_at, 'weekday 0', '-6 days') AS week, SUM(minutes) AS minutes FROM mission_completions GROUP BY week ORDER BY week DESC LIMIT 8"
        ).fetchall()
        return [(row["week"], row["minutes"]) for row in rows]
