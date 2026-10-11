"""Mission generation using Ollama when available and a deterministic local library otherwise."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from services.llm_service import LLMService, OllamaError


VALID_TIMES = (5, 15, 30, 60)
VALID_ENVIRONMENTS = ("park", "garden", "campus", "neighborhood", "hiking trail")
VALID_DIFFICULTIES = ("beginner", "intermediate", "advanced")
VALID_INTERESTS = ("birds", "plants", "insects", "trees", "photography", "general nature")


@dataclass
class MissionService:
    llm: LLMService
    library_path: Path = Path(__file__).parent.parent / "data" / "offline_missions.json"

    def generate(self, minutes: int, environment: str, difficulty: str, interest: str) -> tuple[dict[str, Any], bool]:
        self._validate(minutes, environment, difficulty, interest)
        try:
            result = self.llm.chat(
                [
                    {
                        "role": "system",
                        "content": (
                            "You create safe, screen-light outdoor missions. Return strict JSON with keys "
                            "title, description, tasks (list), duration_minutes, difficulty, observation_tips (list), "
                            "reflection_question. Never advise eating unknown plants or handling wildlife."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Create a {minutes}-minute {difficulty} mission in a {environment} focused on {interest}.",
                    },
                ]
            )
            mission = json.loads(result)
            return self._normalize(mission, minutes, difficulty), True
        except (OllamaError, json.JSONDecodeError, TypeError, KeyError, ValueError):
            return self._offline(minutes, environment, difficulty, interest), False

    @staticmethod
    def _validate(minutes: int, environment: str, difficulty: str, interest: str) -> None:
        if minutes not in VALID_TIMES:
            raise ValueError("Minutes must be one of 5, 15, 30, or 60.")
        if environment not in VALID_ENVIRONMENTS:
            raise ValueError("Choose a supported environment.")
        if difficulty not in VALID_DIFFICULTIES:
            raise ValueError("Choose a supported difficulty.")
        if interest not in VALID_INTERESTS:
            raise ValueError("Choose a supported interest.")

    @staticmethod
    def _normalize(mission: dict[str, Any], minutes: int, difficulty: str) -> dict[str, Any]:
        required = ("title", "description", "tasks", "observation_tips", "reflection_question")
        if any(not mission.get(key) for key in required):
            raise ValueError("The model returned an incomplete mission.")
        return {
            "title": str(mission["title"])[:120],
            "description": str(mission["description"])[:500],
            "tasks": [str(item) for item in mission["tasks"][:8]],
            "duration_minutes": minutes,
            "difficulty": difficulty,
            "observation_tips": [str(item) for item in mission["observation_tips"][:6]],
            "reflection_question": str(mission["reflection_question"])[:300],
        }

    def _offline(self, minutes: int, environment: str, difficulty: str, interest: str) -> dict[str, Any]:
        data = json.loads(self.library_path.read_text(encoding="utf-8"))
        candidates = [
            item for item in data
            if item["duration_minutes"] == minutes
            and (item["interest"] == interest or interest == "general nature")
        ]
        item = candidates[0] if candidates else data[0]
        mission = dict(item)
        mission["title"] = f"{mission['title']} · {environment.title()}"
        mission["difficulty"] = difficulty
        return mission
