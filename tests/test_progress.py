from database.db import Database
from database.progress_repository import ProgressRepository


def test_progress_summary_and_duplicate_guard(tmp_path):
    progress = ProgressRepository(Database(tmp_path / "progress.db").connection())
    progress.record_mission("Walk", 15, "birds")
    progress.record_mission("Walk", 15, "birds")
    summary = progress.summary()
    assert summary["missions"] == 1
    assert summary["minutes"] == 15
    assert summary["categories"] == 1
