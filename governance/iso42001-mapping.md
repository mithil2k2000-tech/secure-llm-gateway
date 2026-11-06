# ISO/IEC 42001:2023 (AI management system): alignment

This is not a certification claim. It shows where this project produces evidence an AI management system would need.

| ISO/IEC 42001 area | Evidence in this repo |
|---|---|
| Clause 4: context of the organisation, scope | System card purpose, users and out-of-scope uses |
| Clause 5: leadership, AI policy, roles | Owners in risk register; prohibited uses |
| Clause 6: planning, AI risk assessment and treatment, AI system impact assessment | `risk-register.md`; `eu-ai-act-assessment.md`; `dpia.md` |
| Clause 8: operation | Controls in `app/`; deployment hardening in `Dockerfile` and `docker-compose.yml` |
| Clause 9: performance evaluation | Red-team and benign evaluations in CI; audit log verification |
| Clause 10: improvement | Known gaps tracked (OB-05); incident procedure feeds new eval cases |
| Annex A.2: policies related to AI | System card scope and prohibited uses |
| Annex A.3: internal organisation | Role-based owners; incident roles |
| Annex A.4: resources for AI systems | Documented providers, data and tooling (README, system card) |
| Annex A.5: assessing impacts of AI systems | EU AI Act screening; DPIA; risk register |
| Annex A.6: AI system life cycle | ADRs; CI gates; change control on provider/model changes |
| Annex A.7: data for AI systems | Corpus labels; ingest scan and quarantine; PII handling |
| Annex A.8: information for interested parties | System card; user AI disclosure |
| Annex A.9: use of AI systems | Intended use and prohibited uses; audit review |
| Annex A.10: third-party and customer relationships | Provider choice and data-transfer notes in the DPIA |
