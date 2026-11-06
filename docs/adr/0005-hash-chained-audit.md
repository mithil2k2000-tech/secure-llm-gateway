# ADR-0005: Hash-chained audit log that stores prompt hashes by default

**Status:** Accepted

## Context
Investigating misuse needs a trustworthy record of who asked what and what the system did. Storing raw prompts creates a new store of personal data.

## Decision
- Write one JSON line per request with: user, role, provider, retrieved and cited documents, guardrail decisions and latency.
- Store the SHA-256 of the question. Raw text is opt-in.
- Include the previous record's hash in each record. Edits and deletions are detectable with `audit.verify`.

## Consequences
- Tampering inside the file is detectable. Truncating the tail is not, so production should ship records to write-once storage (for example an immutable blob container or a SIEM).
- With hashes only, investigators can confirm a known prompt was asked but cannot read unknown prompts. That trade-off is set by `AUDIT_LOG_RAW_PROMPTS`.
