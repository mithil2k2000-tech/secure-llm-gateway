# Data protection impact assessment (screening), UK GDPR

| Item | Assessment |
|---|---|
| Processing | Employees' questions; retrieval over internal documents, some containing personal data (HR records) |
| Data subjects | Employees asking questions; employees named in HR documents |
| Personal data | Identifiers in questions (by accident or design); HR contact records (HR-only label) |
| Special category data | Not intended. Users are told not to enter health or other special category data. |
| Purpose and lawful basis | Helping staff find policy information. Legitimate interests (Art. 6(1)(f)); a balancing test is recorded by the deployer. |
| Necessity and minimisation | PII redacted from questions before model calls and from answers; prompts logged as SHA-256 hashes by default; HR data restricted by role |
| Retention | Audit log retained for 12 months (deployer to confirm), then deleted; no conversation history stored |
| Processors and transfers | Mock and Ollama: no third party. Anthropic API: the redacted question and retrieved document text go to Anthropic. Requires a data processing agreement and, where data leaves the UK, a transfer mechanism and transfer risk assessment. Prefer Ollama for HR-labelled content. |
| Rights | Access and erasure requests: audit records are keyed by user ID; prompt text is not stored by default |
| Security | Authentication, role-based retrieval, TLS at the ingress (deployer), non-root read-only container, hash-chained audit, dependency and image scanning |
| Automated decisions (Art. 22) | None. The system makes no decisions with legal or similarly significant effects. |
| Residual risk | Low to medium, driven by R5/R6 in the risk register. No prior consultation with the ICO needed at this level. |

Review when the provider, data sources or purpose change.
