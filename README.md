# Secure LLM Gateway

A retrieval-augmented policy assistant built secure by design, with an AI governance pack. It shows how to stop the OWASP Top 10 for LLM Applications (2025) risks with layered controls, and how to prove it with a red-team suite that gates every pull request.

![CI](../../actions/workflows/ci.yml/badge.svg)

## Results

The 25-attack suite runs with guardrails off and on, against a deliberately gullible model (see [ADR-0004](docs/adr/0004-gullible-mock-for-evaluation.md)):

| | No guardrails | Guardrails on |
|---|---|---|
| Attack success rate | 100% | **4%** (1 documented known gap) |
| Benign questions answered correctly | 93% | **100%** |

Full per-attack table: [eval/results/report.md](eval/results/report.md).

The one attack that gets through (OB-05) is a paraphrased injection the heuristic doesn't know. It is recorded rather than tuned away, because the design assumes the detector will be bypassed ([ADR-0002](docs/adr/0002-defence-in-depth.md)). Even then, the other layers mean all it can make the assistant say is a harmless string.

## Controls

| Layer | Control | OWASP LLM |
|---|---|---|
| API | API-key auth (hashed), per-user rate limit, size limits, security headers, kill switch | LLM10 |
| Input | Unicode/zero-width/base64/leetspeak normalisation, injection heuristic, PII redaction before the model | LLM01, LLM02 |
| Retrieval | **Role-based filtering before ranking**, ingest-time quarantine of instruction-like chunks | LLM02, LLM04, LLM08 |
| Prompt | Per-request canary, untrusted text fenced and marked as data | LLM01, LLM07 |
| Output | Leak detection (canary and verbatim overlap), image removal, link allow-list, PII redaction, citation validation, HTML escaping | LLM05, LLM07, LLM09 |
| Audit | Hash-chained JSONL with prompt hashes; admin verify endpoint | — |
| Supply chain | Pinned deps, pip-audit, Bandit, Gitleaks, Trivy image scan, non-root read-only container | LLM03 |
| Agency | No tools or actions by design | LLM06 |

## Governance pack

- [AI system card](governance/ai-system-card.md): purpose, users, prohibited uses, limitations, oversight
- [Risk register](governance/risk-register.md): 15 risks scored before and after controls
- [OWASP LLM Top 10 coverage](governance/owasp-llm-top10.md)
- [NIST AI RMF](governance/nist-ai-rmf.md): Govern, Map, Measure, Manage
- [EU AI Act screening](governance/eu-ai-act-assessment.md): not high-risk as scoped; transparency duty
- [ISO/IEC 42001 alignment](governance/iso42001-mapping.md)
- [DPIA screening (UK GDPR)](governance/dpia.md)
- [AI incident response](governance/incident-response.md)
- [Architecture](docs/architecture.md) and [ADRs](docs/adr/)

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/make_demo_keys.py          # prints 4 demo keys, stores only hashes
uvicorn app.main:app --port 8000

curl -s localhost:8000/v1/ask -H "X-API-Key: <alice's key>" -H 'content-type: application/json' \
  -d '{"question": "What is the meal allowance when travelling overnight?"}'
```

Checks:

```bash
pytest -q                 # 20 unit and API tests
python -m eval.run        # red-team suite and gate (exit 1 on failure)
ruff check . && bandit -c pyproject.toml -r app eval scripts && pip-audit -r requirements.txt
```

### Providers

| `LLM_PROVIDER` | Cost | Notes |
|---|---|---|
| `mock` (default) | free | Gullible simulator for tests and evaluation |
| `ollama` | free | Local open-weight model, e.g. `LLM_MODEL=llama3.2:3b`; data stays on your machine |
| `anthropic` | paid API | Set `ANTHROPIC_API_KEY`; see the DPIA before sending real data |

Container: `docker compose up --build`. The service binds to localhost and runs as non-root with a read-only filesystem.

## Layout

```
app/            API, pipeline, guardrails, retrieval, providers, audit
data/docs/      sample corpus (fictional Acme Ltd) incl. two poisoned documents and fake PII
eval/           attack and benign cases, runner and gate, latest report
tests/          unit and API tests
governance/     AI governance pack
docs/           architecture and ADRs
```

## AI assistance

An AI assistant (Claude, Anthropic) helped write the code and documents. The author designed the system and reviewed the code and results.
