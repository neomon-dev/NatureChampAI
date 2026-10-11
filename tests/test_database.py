from database.db import Database
from database.journal_repository import JournalRepository


def test_sqlite_initialization_and_journal_crud(tmp_path):
    journal = JournalRepository(Database(tmp_path / "test.db").connection())
    entry = {"entry_date": "2026-10-11", "location_label": "Garden", "title": "Bee", "notes": "A bee visited lavender."}
    entry_id = journal.create(entry)
    assert journal.get(entry_id)["title"] == "Bee"
    journal.update(entry_id, {**entry, "title": "Bee update"})
    assert journal.get(entry_id)["title"] == "Bee update"
    assert len(journal.list("lavender")) == 1
    journal.delete(entry_id)
    assert journal.get(entry_id) is None
