from __future__ import annotations

from app.providers.anthropic import AnthropicProvider
from app.providers.naive_mock import NaiveMockProvider
from app.providers.ollama import OllamaProvider


def get(name: str, model: str = ""):
    if name == "mock":
        return NaiveMockProvider()
    if name == "ollama":
        return OllamaProvider(model)
    if name == "anthropic":
        return AnthropicProvider(model)
    raise ValueError(f"unknown provider {name!r}; use mock, ollama or anthropic")
