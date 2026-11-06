"""Anthropic Messages API. The key is read from ANTHROPIC_API_KEY at call time and never logged."""

from __future__ import annotations

import os

import httpx


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, model: str = ""):
        self.model = model or os.environ.get("ANTHROPIC_MODEL", "claude-haiku-5-5")

    def generate(self, system: str, user: str, max_tokens: int) -> str:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": 0,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=60,
        )
        r.raise_for_status()
        return "".join(b.get("text", "") for b in r.json()["content"] if b.get("type") == "text")
