# ADR-0006: Quarantine instruction-like chunks at ingest

**Status:** Accepted

## Context
Indirect prompt injection arrives through documents (OWASP LLM01 and LLM04). The corpus is semi-trusted: many authors contribute, and suppliers and other outside parties supply content.

## Decision
- Score every chunk with the injection heuristic at ingest.
- Keep flagged chunks for review, but never serve them while guardrails are on.
- Clean paragraphs of the same document are still served.

## Consequences
- II-01 (fake payment instructions) and II-02 (tracking-image exfiltration) are stopped before the model sees them.
- False positives hide legitimate paragraphs, for example a security policy that quotes an attack. Owners need a review queue to release them.
- Chunks that evade the scanner still face spotlighting and output checks.
