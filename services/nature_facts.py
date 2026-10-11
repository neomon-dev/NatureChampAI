"""Curated offline nature facts."""

import json
from pathlib import Path


def load_facts() -> list[dict[str, str]]:
    path = Path(__file__).parent.parent / "data" / "nature_facts.json"
    return json.loads(path.read_text(encoding="utf-8"))
