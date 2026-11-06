# AI system card: Acme policy assistant (Secure LLM Gateway)

| | |
|---|---|
| Version | 0.1.0 |
| Owner | Product owner (named in deployment) |
| Risk tier (internal) | Limited risk: answers questions; makes no decisions about people |
| EU AI Act | Not high-risk as scoped; transparency duty applies (see [eu-ai-act-assessment.md](eu-ai-act-assessment.md)) |
| Last evaluation | See `eval/results/report.md`; runs on every pull request |

## Purpose
Answers employees' questions about internal policies (leave, expenses, travel, IT security) using only documents they are allowed to see, and cites its sources.

## Intended users
Employees of the deploying organisation, authenticated, each with a role: employee, engineer, hr or admin.

## Out of scope (must not be used for)
- Any decision about an individual: hiring, performance, pay, discipline, dismissal or task allocation. Using it this way would make the system high-risk under EU AI Act Annex III (employment).
- Legal, medical or financial advice to individuals.
- Retrieving personal data about colleagues. NI numbers, card numbers, phone numbers and emails are redacted from answers for every role.

## How it works
- Retrieval is filtered by the caller's role **before** ranking.
- Untrusted document text is fenced and marked as data. Document chunks that look like instructions are quarantined at ingest.
- The model answers using one of three providers:
  - **mock**: a deliberately gullible simulator;
  - **ollama**: a local open-weight model;
  - **anthropic**: the Claude API.
- Output is checked for system-prompt leakage (a per-request canary token and verbatim overlap), images, unapproved links, PII, invented citations and HTML.
- Every request is written to a hash-chained audit log, which stores prompt hashes rather than text by default.

## Data
- **Corpus:** markdown files with a classification label each.
- **Questions:** may contain personal data. PII is redacted before the question reaches the model, and only the question's hash is logged unless raw logging is switched on.
- **Third-party processing:** with the Anthropic provider, the redacted question and the retrieved document text are sent to the API. See [dpia.md](dpia.md).

## Evaluation
- 25 attacks mapped to the OWASP Top 10 for LLM Applications (2025) and 14 benign questions, run with guardrails off and on.
- Against the gullible mock:
  - attack success rate is 100% without guardrails and 4% with them (1 documented known gap, OB-05);
  - all 14 benign questions are answered correctly.
- The mock is a pessimistic stand-in. Re-run with the production provider before go-live and after any model change.

## Known limitations
- The prompt-injection heuristic catches known phrasings and common obfuscation but not paraphrases (OB-05). The architecture assumes it will be bypassed.
- PII patterns are UK-specific. Names and addresses are not detected.
- BM25 retrieval misses synonyms, so some valid questions may get "I don't know".
- Rate limiting is per process. Run behind a gateway with shared limits if you scale out.

## Human oversight
- Answers carry citations so users can check the source.
- Blocked requests and their reasons are in the audit log for review.
- The kill switch `GATEWAY_DISABLED=true` stops all model calls without a code change.
- Changing the provider or model requires a passing red-team evaluation, enforced by the CI gate.

## Contact
Issues and incidents: see [incident-response.md](incident-response.md).
