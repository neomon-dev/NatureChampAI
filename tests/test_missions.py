import json
from pathlib import Path

import pytest

from services.llm_service import OllamaError
from services.mission_service import MissionService


class FakeLLM:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def chat(self, messages):
        if self.error:
            raise self.error
        return self.response


def test_offline_mission_fallback():
    mission, generated = MissionService(FakeLLM(error=OllamaError("offline"))).generate(5, "park", "beginner", "general nature")
    assert generated is False
    assert mission["duration_minutes"] == 5
    assert mission["tasks"]


def test_ai_mission_is_normalized():
    payload = json.dumps({"title": "Model walk", "description": "Notice edges.", "tasks": ["Walk"], "observation_tips": ["Stay back"], "reflection_question": "What changed?"})
    mission, generated = MissionService(FakeLLM(response=payload)).generate(15, "garden", "intermediate", "plants")
    assert generated is True
    assert mission["duration_minutes"] == 15


def test_invalid_mission_inputs_are_rejected():
    with pytest.raises(ValueError):
        MissionService(FakeLLM()).generate(7, "park", "beginner", "birds")
