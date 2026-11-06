# AI risk register

Scoring: Likelihood (L) and Impact (I) are each rated 1 to 5; Risk = L × I. Residual scores assume the controls are in place. Owners are roles, not people.

| ID | Risk | OWASP LLM | L | I | Inherent | Controls | Residual | Owner |
|---|---|---|---|---|---|---|---|---|
| R1 | Direct prompt injection makes the assistant ignore its rules | LLM01 | 4 | 3 | 12 | Normalisation and heuristic input filter; system prompt rules; output checks; eval gate | 4 | Engineering |
| R2 | Paraphrased or novel injection evades the input filter | LLM01 | 4 | 3 | 12 | Defence in depth: access control, quarantine and output checks make a successful injection low-value; known gap OB-05 tracked | 6 | Engineering |
| R3 | Poisoned document (indirect injection) changes answers or exfiltrates data | LLM01, LLM04 | 3 | 4 | 12 | Ingest scan and quarantine; spotlighting; image and link removal; document owners approve corpus changes | 4 | Content owner |
| R4 | User retrieves documents above their clearance | LLM02, LLM08 | 3 | 5 | 15 | Role filter applied in retrieval before ranking; tests assert no chunk above clearance is returned | 2 | Engineering |
| R5 | Personal data disclosed in answers | LLM02 | 3 | 5 | 15 | Output PII redaction for all roles; HR data kept in HR-only label; DPIA | 4 | DPO |
| R6 | Users' PII sent to a third-party model provider | LLM02 | 4 | 3 | 12 | Input PII redaction; provider choice documented; local Ollama option; contract and transfer assessment before using a cloud API | 4 | DPO |
| R7 | System prompt or configuration leaked | LLM07 | 4 | 2 | 8 | Per-request canary; overlap check; no secrets in the prompt by design | 2 | Engineering |
| R8 | Answer renders active content (script, tracking image, phishing link) | LLM05 | 3 | 4 | 12 | HTML escaping; image removal; link allow-list; CSP on API responses | 2 | Engineering |
| R9 | Incorrect or invented answer relied on (hallucination) | LLM09 | 3 | 3 | 9 | Answer only from documents; citations required and validated; "I don't know" path; users told to check sources | 6 | Product owner |
| R10 | Cost or availability abuse | LLM10 | 3 | 3 | 9 | Input length limits; per-user rate limit; max output tokens; budget alerts at the provider | 3 | Engineering |
| R11 | Vulnerable dependency or container | LLM03 | 3 | 4 | 12 | Pinned requirements; pip-audit; Trivy image scan; Bandit; non-root, read-only container | 4 | Engineering |
| R12 | Assistant given tools or actions beyond its purpose | LLM06 | 2 | 5 | 10 | No tools or actions by design (ADR-0003); any future tool needs a new risk assessment | 2 | Product owner |
| R13 | Misuse for decisions about individuals (scope creep into high-risk) | n/a | 2 | 5 | 10 | Out-of-scope uses in system card and user notice; periodic use review of audit logs | 4 | Product owner |
| R14 | Audit trail altered to hide misuse | n/a | 2 | 4 | 8 | Hash-chained log with admin-only verify endpoint; ship to write-once storage in production | 3 | Security |
| R15 | Model change silently degrades safety | LLM01–LLM10 | 3 | 4 | 12 | Red-team suite and benign suite gate every change; re-run on provider or model change | 4 | Engineering |

Review this register quarterly, and after any incident, model change or new data source.
