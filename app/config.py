"""Runtime settings, read from environment variables only (no secrets in code)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Which document labels each role may retrieve. Enforced in retrieval, before the model sees anything.
ROLE_CLEARANCE: dict[str, frozenset[str]] = {
    "employee": frozenset({"public", "internal"}),
    "engineer": frozenset({"public", "internal", "engineering"}),
    "hr": frozenset({"public", "internal", "hr-confidential"}),
    "admin": frozenset({"public", "internal", "engineering", "hr-confidential"}),
}


def _int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


def _float(name: str, default: float) -> float:
    return float(os.environ.get(name, default))


@dataclass(frozen=True)
class Settings:
    provider: str = field(default_factory=lambda: os.environ.get("LLM_PROVIDER", "mock"))
    model: str = field(default_factory=lambda: os.environ.get("LLM_MODEL", ""))
    max_input_chars: int = field(default_factory=lambda: _int("MAX_INPUT_CHARS", 2000))
    max_output_tokens: int = field(default_factory=lambda: _int("MAX_OUTPUT_TOKENS", 512))
    top_k: int = field(default_factory=lambda: _int("RETRIEVAL_TOP_K", 3))
    injection_threshold: float = field(default_factory=lambda: _float("INJECTION_THRESHOLD", 0.5))
    rate_per_minute: int = field(default_factory=lambda: _int("RATE_LIMIT_PER_MINUTE", 20))
    docs_dir: Path = field(default_factory=lambda: Path(os.environ.get("DOCS_DIR", ROOT / "data" / "docs")))
    audit_path: Path = field(default_factory=lambda: Path(os.environ.get("AUDIT_LOG", ROOT / "audit" / "audit.jsonl")))
    users_file: Path = field(default_factory=lambda: Path(os.environ.get("USERS_FILE", ROOT / "data" / "users.json")))
    # Links in answers may only point at these hosts (blocks markdown-image data exfiltration).
    allowed_link_hosts: frozenset[str] = field(
        default_factory=lambda: frozenset(
            h.strip() for h in os.environ.get("ALLOWED_LINK_HOSTS", "intranet.example.com").split(",") if h.strip()
        )
    )
    # Kill switch: refuse all model calls without redeploying code (NIST AI RMF MANAGE 2.4).
    disabled: bool = field(default_factory=lambda: os.environ.get("GATEWAY_DISABLED", "false") == "true")
    log_raw_prompts: bool = field(default_factory=lambda: os.environ.get("AUDIT_LOG_RAW_PROMPTS", "false") == "true")
