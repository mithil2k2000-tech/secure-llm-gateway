"""Load the document corpus. Each markdown file starts with a small front-matter block:

---
id: expenses-policy
title: Expenses policy
labels: internal
---
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.guardrails import injection

FRONT = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    title: str
    label: str
    text: str
    chunk_no: int
    ingest_flags: tuple[str, ...] = ()

    @property
    def ref(self) -> str:
        return f"doc:{self.doc_id}"


def _parse(path: Path) -> tuple[dict[str, str], str]:
    m = FRONT.match(path.read_text(encoding="utf-8"))
    if not m:
        raise ValueError(f"{path.name}: missing front matter")
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    return {k.strip(): v.strip() for k, v in meta.items()}, m.group(2).strip()


def load(docs_dir: Path, *, scan_threshold: float = 0.5) -> list[Chunk]:
    """Split each document into paragraph chunks. Chunks that look like instructions are flagged at ingest
    (OWASP LLM04/LLM08). Flagged chunks are quarantined: kept for review but never served while guardrails are on."""
    chunks: list[Chunk] = []
    for path in sorted(docs_dir.glob("*.md")):
        meta, body = _parse(path)
        for i, para in enumerate(p.strip() for p in body.split("\n\n") if p.strip()):
            res = injection.score(para)
            flags = ("suspected_injection",) if res.flagged(scan_threshold) else ()
            chunks.append(Chunk(meta["id"], meta.get("title", meta["id"]), meta["labels"], para, i, flags))
    return chunks
