"""Generate demo API keys: prints the keys once and writes only their SHA-256 hashes to data/users.json."""

import hashlib
import json
import secrets
from pathlib import Path

USERS = [("alice", "employee"), ("eve", "engineer"), ("hana", "hr"), ("adam", "admin")]
out, shown = [], []
for user, role in USERS:
    key = "sk-demo-" + secrets.token_urlsafe(24)
    out.append({"user_id": user, "role": role, "key_sha256": hashlib.sha256(key.encode()).hexdigest()})
    shown.append(f"{user:6} {role:9} {key}")
Path("data/users.json").write_text(json.dumps(out, indent=2) + "\n")
print("Demo keys (shown once, not stored):\n" + "\n".join(shown))
