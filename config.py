"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    ollama_vision_model: str = os.getenv("OLLAMA_VISION_MODEL", "").strip()
    database_path: Path = Path(os.getenv("NATUREBUDDY_DB_PATH", "naturebuddy.db"))
    max_image_size_mb: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "8"))


settings = Settings()
