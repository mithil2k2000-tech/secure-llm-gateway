"""UK-focused PII detection and redaction (regex plus checksum validation where one exists)."""

from __future__ import annotations

import re
from dataclasses import dataclass


def _luhn(digits: str) -> bool:
    nums = [int(d) for d in digits][::-1]
    total = sum(nums[0::2]) + sum(sum(divmod(2 * d, 10)) for d in nums[1::2])
    return total % 10 == 0


@dataclass(frozen=True)
class PiiType:
    name: str
    pattern: re.Pattern[str]
    validate: object = None  # optional callable(str) -> bool


TYPES = [
    PiiType("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    PiiType(
        "NI_NUMBER",
        re.compile(r"\b(?!BG|GB|NK|KN|TN|NT|ZZ)[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z] ?\d{2} ?\d{2} ?\d{2} ?[A-D]\b", re.I),
    ),
    PiiType(
        "CARD",
        re.compile(r"\b(?:\d[ -]?){13,19}\b"),
        lambda m: _luhn(re.sub(r"\D", "", m)) and 13 <= len(re.sub(r"\D", "", m)) <= 19,
    ),
    PiiType("UK_IBAN", re.compile(r"\bGB\d{2} ?[A-Z]{4}(?: ?\d{4}){3} ?\d{2}\b")),
    PiiType("SORT_CODE", re.compile(r"\b\d{2}-\d{2}-\d{2}\b")),
    PiiType("UK_PHONE", re.compile(r"(?:\+44 ?7\d{3}|\b07\d{3}) ?\d{3} ?\d{3}\b")),
]


@dataclass(frozen=True)
class PiiFinding:
    kind: str
    start: int
    end: int


def find(text: str) -> list[PiiFinding]:
    findings: list[PiiFinding] = []
    for t in TYPES:
        for m in t.pattern.finditer(text):
            if t.validate and not t.validate(m.group()):
                continue
            if any(f.start < m.end() and m.start() < f.end for f in findings):
                continue
            findings.append(PiiFinding(t.name, m.start(), m.end()))
    return sorted(findings, key=lambda f: f.start)


def redact(text: str) -> tuple[str, list[str]]:
    findings = find(text)
    out, last = [], 0
    for f in findings:
        out.append(text[last : f.start])
        out.append(f"[REDACTED:{f.kind}]")
        last = f.end
    out.append(text[last:])
    return "".join(out), [f.kind for f in findings]
