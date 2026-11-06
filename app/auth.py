"""API-key authentication for the demo. Only SHA-256 hashes of keys are stored (data/users.json).

In production, replace with Entra ID / OIDC and map group claims to roles.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path

from app.config import ROLE_CLEARANCE


@dataclass(frozen=True)
class User:
    user_id: str
    role: str

    @property
    def clearance(self) -> frozenset[str]:
        return ROLE_CLEARANCE[self.role]


class KeyStore:
    def __init__(self, path: Path):
        self.entries = json.loads(path.read_text()) if path.exists() else []
        for e in self.entries:
            if e["role"] not in ROLE_CLEARANCE:
                raise ValueError(f"unknown role {e['role']!r} for {e['user_id']}")

    def authenticate(self, key: str | None) -> User | None:
        if not key:
            return None
        digest = hashlib.sha256(key.encode()).hexdigest()
        match = None
        for e in self.entries:  # compare against every entry to keep timing constant
            if hmac.compare_digest(digest, e["key_sha256"]):
                match = e
        return User(match["user_id"], match["role"]) if match else None
