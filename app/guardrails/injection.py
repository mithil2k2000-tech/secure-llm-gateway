"""Heuristic prompt-injection scorer.

This is deliberately one layer of several. The author's own study of lightweight detectors found they generalise
poorly across datasets and are easy to evade, so nothing in this app relies on this score alone: retrieval access
control, spotlighting of untrusted text, a canary for system-prompt leakage and output filtering all run regardless.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.guardrails.normalise import deleet, normalise

# (pattern, weight). Weights add up and are capped at 1.0.
PATTERNS: list[tuple[re.Pattern[str], float]] = [
    (re.compile(p), w)
    for p, w in [
        (
            r"\b(ignore|disregard|forget|override)\b.{0,40}\b(previous|prior|above|earlier|all|system|your)\b.{0,20}"
            r"\b(instructions?|prompts?|rules?|guidelines?|directions?)",
            0.7,
        ),
        (r"\b(system prompt|initial prompt|hidden prompt|your instructions|the text above|developer message)\b", 0.4),
        (r"\b(reveal|print|repeat|show|output|display|leak)\b.{0,30}\b(prompt|instructions|rules|canary|secret)", 0.4),
        (r"\byou are (now|no longer)\b|\bact as\b|\bpretend (to be|you are)\b|\broleplay as\b", 0.35),
        (r"\b(dan|developer mode|jailbreak|do anything now|god mode)\b", 0.5),
        (r"\bnew instructions?\b|\binstead,? (you will|do|say)\b|\bfrom now on\b", 0.35),
        (r"!\[[^\]]*\]\(https?://", 0.5),  # markdown image, classic exfiltration channel
        (r"<\s*(script|iframe|img)\b", 0.4),
        (r"\b(begin|end) (system|admin|developer)\b|\[/?(system|inst)\]|<\|?(im_start|system)\|?>", 0.5),
        (r"\b(salary bands?|all salaries|everyone'?s salary|confidential (data|documents?))\b", 0.2),
    ]
]


@dataclass(frozen=True)
class InjectionResult:
    score: float
    matched: tuple[str, ...]

    def flagged(self, threshold: float) -> bool:
        return self.score >= threshold


def score(text: str) -> InjectionResult:
    norm = normalise(text)
    variants = {norm, deleet(norm)}
    total, matched = 0.0, []
    for pattern, weight in PATTERNS:
        if any(pattern.search(v) for v in variants):
            total += weight
            matched.append(pattern.pattern[:40])
    return InjectionResult(min(total, 1.0), tuple(matched))
