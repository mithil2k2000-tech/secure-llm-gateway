"""The request pipeline, independent of HTTP so the red-team evaluation can drive it directly.

input checks -> access-controlled retrieval -> spotlighted prompt -> model -> output checks -> audit
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field

from app import audit, prompt
from app.auth import User
from app.config import ROLE_CLEARANCE, Settings
from app.documents import Chunk
from app.guardrails import injection, output, pii
from app.retrieval import Index

REFUSAL_INJECTION = "Your request looks like an attempt to change my instructions, so I can't process it."
REFUSAL_TOO_LONG = "Your question is too long. Please shorten it."


@dataclass
class Answer:
    request_id: str
    answer: str
    citations: list[str] = field(default_factory=list)
    blocked: bool = False
    reasons: list[str] = field(default_factory=list)
    retrieved: list[str] = field(default_factory=list)
    injection_score: float = 0.0

    def public(self) -> dict:
        d = asdict(self)
        d.pop("retrieved")
        return d


class Pipeline:
    def __init__(self, settings: Settings, index: Index, provider, *, guardrails: bool = True):
        self.s, self.index, self.provider, self.guardrails = settings, index, provider, guardrails

    def ask(self, user: User, question: str) -> Answer:
        start = time.perf_counter()
        rid = str(uuid.uuid4())
        ans = self._run(rid, user, question)
        audit.write(
            self.s.audit_path,
            {
                "request_id": rid,
                "user": user.user_id,
                "role": user.role,
                "provider": self.provider.name,
                "guardrails": self.guardrails,
                "question_sha256": audit.sha256(question),
                **({"question": question} if self.s.log_raw_prompts else {}),
                "injection_score": round(ans.injection_score, 2),
                "retrieved": ans.retrieved,
                "citations": ans.citations,
                "blocked": ans.blocked,
                "reasons": ans.reasons,
                "latency_ms": round((time.perf_counter() - start) * 1000, 1),
            },
        )
        return ans

    def _run(self, rid: str, user: User, question: str) -> Answer:
        reasons: list[str] = []
        if self.guardrails:
            if len(question) > self.s.max_input_chars:
                return Answer(rid, REFUSAL_TOO_LONG, blocked=True, reasons=["input_too_long"])
            inj = injection.score(question)
            if inj.flagged(self.s.injection_threshold):
                return Answer(rid, REFUSAL_INJECTION, blocked=True, reasons=["input_injection"], injection_score=inj.score)
            question, kinds = pii.redact(question)  # don't send users' own PII to a third-party model
            if kinds:
                reasons.append("input_pii_redacted:" + ",".join(sorted(set(kinds))))
            clearance = user.clearance
        else:
            inj = injection.score(question)
            clearance = frozenset().union(*ROLE_CLEARANCE.values())  # baseline: no access control

        chunks: list[Chunk] = self.index.search(question, clearance, self.s.top_k, exclude_flagged=self.guardrails)
        canary = prompt.new_canary()
        system = prompt.system_prompt(canary)
        if self.guardrails:
            user_msg = prompt.user_turn(question, chunks)
        else:  # baseline: no fencing, no warnings
            user_msg = "Documents:\n" + "\n\n".join(f'<document ref="{c.ref}">\n{c.text}\n</document>' for c in chunks)
            user_msg += f"\n\nQuestion: {question}"

        raw = self.provider.generate(system, user_msg, self.s.max_output_tokens)
        retrieved = [c.ref for c in chunks]
        if not self.guardrails:
            return Answer(rid, raw, retrieved=retrieved, injection_score=inj.score)

        out = output.check(
            raw, canary=canary, allowed_hosts=self.s.allowed_link_hosts, retrieved_ids=set(retrieved), system_prompt=system
        )
        return Answer(rid, out.text, out.citations, out.blocked, reasons + out.reasons, retrieved, inj.score)
