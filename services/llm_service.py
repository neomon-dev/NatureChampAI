"""Local Ollama language-model integration with explicit failures."""

from dataclasses import dataclass
from typing import Any

import requests

from config import Settings, settings


class OllamaError(RuntimeError):
    """Raised when Ollama cannot provide a valid response."""


@dataclass
class LLMService:
    config: Settings = settings
    timeout: float = 45.0

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.config.ollama_base_url}/api/tags", timeout=5)
            return response.ok
        except requests.RequestException:
            return False

    def available_models(self) -> list[str]:
        try:
            response = requests.get(f"{self.config.ollama_base_url}/api/tags", timeout=5)
            response.raise_for_status()
            payload = response.json()
            return [item.get("name", "") for item in payload.get("models", []) if item.get("name")]
        except (requests.RequestException, ValueError) as exc:
            raise OllamaError("Ollama is not reachable.") from exc

    def chat(self, messages: list[dict[str, str]], model: str | None = None) -> str:
        chosen_model = model or self.config.ollama_model
        try:
            tags = self.available_models()
            if chosen_model not in tags:
                raise OllamaError(
                    f"Model '{chosen_model}' is not installed. Install it with: ollama pull {chosen_model}"
                )
            response = requests.post(
                f"{self.config.ollama_base_url}/api/chat",
                json={"model": chosen_model, "messages": messages, "stream": False},
                timeout=self.timeout,
            )
            response.raise_for_status()
            content: Any = response.json().get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                raise OllamaError("Ollama returned an empty response.")
            return content.strip()
        except OllamaError:
            raise
        except (requests.RequestException, ValueError) as exc:
            raise OllamaError("Ollama could not complete the request.") from exc

    def analyze_image(self, prompt: str, image_bytes: bytes, model: str | None = None) -> str:
        chosen_model = model or self.config.ollama_vision_model
        if not chosen_model:
            raise OllamaError("No local vision model is configured.")
        try:
            import base64

            tags = self.available_models()
            if chosen_model not in tags:
                raise OllamaError(
                    f"Vision model '{chosen_model}' is not installed. Install it with: ollama pull {chosen_model}"
                )
            response = requests.post(
                f"{self.config.ollama_base_url}/api/chat",
                json={
                    "model": chosen_model,
                    "messages": [{"role": "user", "content": prompt, "images": [base64.b64encode(image_bytes).decode("ascii")]}],
                    "stream": False,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            content = response.json().get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                raise OllamaError("The vision model returned an empty response.")
            return content.strip()
        except OllamaError:
            raise
        except (requests.RequestException, ValueError) as exc:
            raise OllamaError("The local vision model could not analyze this image.") from exc
