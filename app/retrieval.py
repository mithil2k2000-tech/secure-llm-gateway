"""BM25 retrieval with access control applied *before* ranking.

Filtering by the caller's clearance first means a confidential chunk can never reach the prompt, however the
question is phrased. Asking the model to withhold it would be one prompt injection away from failure.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from app.documents import Chunk

TOKEN = re.compile(r"[a-z0-9]+")
STOP = frozenset(
    "a an the and or of to in on for is are was be what how do does i my we our can with by at it this that".split()  # noqa: SIM905
)


def _stem(t: str) -> str:
    """Very light suffix stripping so 'opening'/'open' and 'offices'/'office' match."""
    if len(t) > 5 and t.endswith("ing"):
        t = t[:-3]
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
        t = t[:-1]
    return t


def tokens(text: str) -> list[str]:
    return [_stem(t) for t in TOKEN.findall(text.lower()) if t not in STOP]


class Index:
    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1, self.b = k1, b
        self.tf = [Counter(tokens(f"{c.title} {c.text}")) for c in chunks]
        self.len = [sum(t.values()) for t in self.tf]
        self.avg = sum(self.len) / max(len(self.len), 1)
        df: Counter[str] = Counter()
        for t in self.tf:
            df.update(t.keys())
        n = len(chunks)
        self.idf = {w: math.log(1 + (n - d + 0.5) / (d + 0.5)) for w, d in df.items()}

    def search(self, query: str, clearance: frozenset[str], k: int = 3, *, exclude_flagged: bool = False) -> list[Chunk]:
        q = tokens(query)
        scored = []
        for i, c in enumerate(self.chunks):
            if c.label not in clearance:  # access control first
                continue
            if exclude_flagged and c.ingest_flags:  # quarantined at ingest
                continue
            s = 0.0
            for w in q:
                f = self.tf[i].get(w, 0)
                if f:
                    s += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
            if s > 0:
                scored.append((s, i))
        scored.sort(reverse=True)
        return [self.chunks[i] for _, i in scored[:k]]
