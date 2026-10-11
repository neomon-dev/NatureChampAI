from unittest.mock import patch

import requests
import pytest

from services.llm_service import LLMService, OllamaError


def test_ollama_connection_failure_is_explicit():
    with patch("services.llm_service.requests.get", side_effect=requests.ConnectionError):
        assert LLMService().is_available() is False


def test_missing_model_is_explicit():
    response = type("Response", (), {"ok": True, "raise_for_status": lambda self: None, "json": lambda self: {"models": []}})()
    with patch("services.llm_service.requests.get", return_value=response):
        with pytest.raises(OllamaError, match="not installed"):
            LLMService().chat([{"role": "user", "content": "hello"}])
