# NIST AI Risk Management Framework (AI RMF 1.0): how this project applies it

| Function | What it asks | How this project does it | Artefact |
|---|---|---|---|
| **Govern** | Policies, roles, accountability and a risk culture are in place (e.g. GOVERN 1: legal and regulatory requirements understood and managed) | Named owners in the risk register; out-of-scope uses defined; AI use disclosed to users; change control through PRs and the CI gate | `risk-register.md`, `ai-system-card.md`, `.github/workflows/ci.yml` |
| **Map** | Context, intended purpose, users and impacts are understood (e.g. MAP 1.1 intended purpose and context; MAP 5 impacts characterised) | Purpose, users and prohibited uses written down; EU AI Act and UK GDPR screening; data flows identified | `ai-system-card.md`, `eu-ai-act-assessment.md`, `dpia.md` |
| **Measure** | Risks are analysed, assessed and tracked with appropriate metrics (e.g. MEASURE 2.7 security and resilience evaluated; MEASURE 2.10 privacy risk examined) | Red-team suite (attack success rate) and benign suite (false refusal rate), baseline vs guarded, on every change; unit tests for each control | `eval/`, `tests/`, `eval/results/report.md` |
| **Manage** | Risks are prioritised, treated and monitored; systems can be disengaged (e.g. MANAGE 2.4 mechanisms to supersede, disengage or deactivate; MANAGE 4.1 post-deployment monitoring) | Risk treatment and residual scores; kill switch `GATEWAY_DISABLED`; hash-chained audit log; incident procedure; quarterly review | `risk-register.md`, `app/main.py`, `app/audit.py`, `incident-response.md` |

The Generative AI Profile (NIST AI 600-1) highlights information security, data privacy and confabulation among GenAI risks. These map to R1–R8, R5–R6 and R9 in the risk register.
