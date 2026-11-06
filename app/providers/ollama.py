"""Local model through Ollama (free, runs on your machine): https://ollama.com."""

from __future__ import annotations

import os

import httpx


class OllamaProvider:
    name = "ollama"

    def __init__(self, model: str = ""):
        self.model = model or "llama3.2:3b"
        self.url = os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/api/chat"

    def generate(self, system: str, user: str, max_tokens: int) -> str:
        r = httpx.post(
            self.url,
            json={
                "model": self.model,
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": 0},
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]
