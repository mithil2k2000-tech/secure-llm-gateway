from __future__ import annotations

from typing import Protocol


class Provider(Protocol):
    name: str

    def generate(self, system: str, user: str, max_tokens: int) -> str: ...
