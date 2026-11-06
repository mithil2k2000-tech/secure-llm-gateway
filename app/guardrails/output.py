"""Checks on model output before it reaches the user (OWASP LLM05 improper output handling, LLM07 leakage)."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from app.guardrails import pii

MD_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)[^)]*\)")
MD_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)[^)]*\)")
BARE_URL = re.compile(r"https?://[^\s)\]>\"']+")
CITATION = re.compile(r"\[(doc:[a-z0-9-]+)\]")


@dataclass
class OutputResult:
    text: str
    blocked: bool = False
    reasons: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)


def check(text: str, *, canary: str, allowed_hosts: frozenset[str], retrieved_ids: set[str], system_prompt: str) -> OutputResult:
    res = OutputResult(text=text)

    # 1. System prompt leakage: the canary only exists in the system prompt.
    lowered = text.lower()
    if canary.lower() in lowered or _overlaps(lowered, system_prompt.lower()):
        return OutputResult(text="I can't share that.", blocked=True, reasons=["system_prompt_leak"])

    # 2. Images are never rendered: they fetch automatically and can carry data in the URL.
    if MD_IMAGE.search(res.text):
        res.text = MD_IMAGE.sub("[image removed]", res.text)
        res.reasons.append("image_removed")

    # 3. Links only to allow-listed hosts.
    def _link(m: re.Match[str]) -> str:
        if _host_ok(m.group(2), allowed_hosts):
            return m.group(0)
        res.reasons.append("link_removed")
        return m.group(1)

    res.text = MD_LINK.sub(_link, res.text)

    def _bare(m: re.Match[str]) -> str:
        if _host_ok(m.group(0), allowed_hosts):
            return m.group(0)
        res.reasons.append("link_removed")
        return "[link removed]"

    res.text = BARE_URL.sub(_bare, res.text)

    # 4. PII redaction on the way out, whatever the source.
    res.text, kinds = pii.redact(res.text)
    if kinds:
        res.reasons.append("pii_redacted:" + ",".join(sorted(set(kinds))))

    # 5. Citations must refer to documents this user was actually given; strip invented ones.
    cited = CITATION.findall(res.text)
    bad = [c for c in cited if c not in retrieved_ids]
    for c in bad:
        res.text = res.text.replace(f"[{c}]", "")
    if bad:
        res.reasons.append("invalid_citation_removed")
    res.citations = sorted({c for c in cited if c in retrieved_ids})

    # 6. Escape HTML so the client cannot be made to run script.
    escaped = html.escape(res.text, quote=False)
    if escaped != res.text:
        res.reasons.append("html_escaped")
    res.text = escaped
    return res


def _host_ok(url: str, allowed: frozenset[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == a or host.endswith("." + a) for a in allowed)


def _overlaps(output: str, system_prompt: str, window: int = 60) -> bool:
    """True if any 60-character run of the system prompt appears verbatim in the output."""
    sp = re.sub(r"\s+", " ", system_prompt)
    out = re.sub(r"\s+", " ", output)
    return any(sp[i : i + window] in out for i in range(0, max(len(sp) - window, 0) + 1, 20))
