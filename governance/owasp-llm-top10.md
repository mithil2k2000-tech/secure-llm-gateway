# OWASP Top 10 for LLM Applications (2025): coverage

| ID | Risk | Controls in this repo | Evidence | Eval cases |
|---|---|---|---|---|
| LLM01 | Prompt injection | Normalisation (NFKC, zero-width, base64, leetspeak) + heuristic filter; spotlighting; ingest quarantine; output checks | `app/guardrails/`, `app/prompt.py`, `app/documents.py` | DI-01–03, OB-01–05, II-01 |
| LLM02 | Sensitive information disclosure | Retrieval access control; PII redaction in and out; hashed prompt logging | `app/retrieval.py`, `app/guardrails/pii.py`, `app/audit.py` | AC-01–04, PII-01–03 |
| LLM03 | Supply chain | Pinned dependencies; pip-audit; Trivy; Bandit; Gitleaks; minimal non-root image | `requirements.txt`, `.github/workflows/ci.yml`, `Dockerfile` | CI |
| LLM04 | Data and model poisoning | Ingest scan and quarantine of instruction-like chunks; corpus under version control and review | `app/documents.py` | II-01, II-02 |
| LLM05 | Improper output handling | HTML escaping; image removal; link allow-list; citation validation; CSP headers | `app/guardrails/output.py`, `app/main.py` | OH-01–03, II-02 |
| LLM06 | Excessive agency | No tools, plugins or write actions by design | ADR-0003 | n/a |
| LLM07 | System prompt leakage | Per-request canary; verbatim-overlap detection; no secrets in prompt | `app/prompt.py`, `app/guardrails/output.py` | SP-01–04 |
| LLM08 | Vector and embedding weaknesses | Access control enforced in the retriever (not the prompt); per-chunk labels; quarantine | `app/retrieval.py` | AC-01–04 |
| LLM09 | Misinformation | Grounding in documents only; required, validated citations; "I don't know" path | `app/prompt.py`, `app/guardrails/output.py` | Benign suite |
| LLM10 | Unbounded consumption | Input length limits (HTTP and pipeline); per-user rate limit; output token cap | `app/main.py`, `app/ratelimit.py`, `app/config.py` | UC-01, `test_rate_limit` |
