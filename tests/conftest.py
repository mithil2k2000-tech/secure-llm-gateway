import hashlib
import json
import os
import tempfile
from pathlib import Path

import pytest

_tmp = Path(tempfile.mkdtemp())
KEYS = {"employee": "test-key-employee", "admin": "test-key-admin", "hr": "test-key-hr"}
(_tmp / "users.json").write_text(
    json.dumps([{"user_id": f"u-{r}", "role": r, "key_sha256": hashlib.sha256(k.encode()).hexdigest()} for r, k in KEYS.items()])
)
os.environ.update(
    {
        "USERS_FILE": str(_tmp / "users.json"),
        "AUDIT_LOG": str(_tmp / "audit.jsonl"),
        "LLM_PROVIDER": "mock",
        "RATE_LIMIT_PER_MINUTE": "1000",
    }
)


@pytest.fixture
def tmp_audit(tmp_path):
    return tmp_path / "audit.jsonl"
