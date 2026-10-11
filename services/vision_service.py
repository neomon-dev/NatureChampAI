"""Local image validation and optional Ollama vision analysis."""

from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from config import Settings, settings
from services.llm_service import LLMService, OllamaError


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_image(image_bytes: bytes, content_type: str, max_size_mb: int = 8) -> tuple[bool, str]:
    if content_type not in ALLOWED_IMAGE_TYPES:
        return False, "Use a JPG, PNG, or WebP image."
    if not image_bytes:
        return False, "The uploaded image is empty."
    if len(image_bytes) > max_size_mb * 1024 * 1024:
        return False, f"Images must be smaller than {max_size_mb} MB."
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        return False, "The file is not a readable image."
    return True, ""


@dataclass
class VisionService:
    llm: LLMService
    config: Settings = settings

    def describe(self, image_bytes: bytes) -> tuple[str, bool]:
        prompt = (
            "Describe this nature image cautiously. Give possible broad identification(s), visible "
            "characteristics, uncertainty, educational facts, and safe observation guidance. Do not "
            "invent a species or scientific name; explicitly say when the image is insufficient."
        )
        try:
            return self.llm.analyze_image(prompt, image_bytes), True
        except OllamaError as exc:
            return f"Local vision analysis is unavailable: {exc}", False
