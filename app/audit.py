"""Append-only, hash-chained audit log (JSON Lines).

Each record stores the SHA-256 of the previous record, so deleting or editing any line breaks the chain and
`verify()` reports where. Prompts are stored as hashes unless AUDIT_LOG_RAW_PROMPTS=true.
"""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import UTC, datetime
from pathlib import Path

GENESIS = "0" * 64
_lock = threading.Lock()


def _digest(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _last_hash(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return GENESIS
    with path.open("rb") as f:
        last = f.readlines()[-1]
    return json.loads(last)["hash"]


def write(path: Path, event: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        record = {"ts": datetime.now(UTC).isoformat(timespec="milliseconds"), **event, "prev": _last_hash(path)}
        record["hash"] = _digest(record)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def verify(path: Path) -> tuple[bool, int, str]:
    """Return (ok, records_checked, message)."""
    if not path.exists():
        return True, 0, "no log yet"
    prev = GENESIS
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        rec = json.loads(line)
        claimed = rec.pop("hash")
        if rec["prev"] != prev:
            return False, n, f"chain broken at record {n}"
        if _digest(rec) != claimed:
            return False, n, f"record {n} was modified"
        prev = claimed
    return True, n if prev != GENESIS else 0, "intact"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()
