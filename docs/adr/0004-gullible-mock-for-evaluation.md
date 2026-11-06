# ADR-0004: Evaluate guardrails against a deliberately gullible model

**Status:** Accepted

## Context
Testing guardrails against a well-aligned model mixes two effects: the model's own refusals and the guardrails'. It also needs paid API calls on every pull request.

## Decision
- Ship a `naive-mock` provider. It answers by extraction but obeys injected instructions: it reveals its prompt, follows "ignore previous instructions", copies images and links, and repeats what it is told.
- CI measures guardrails against it.
- The same suite runs against a real provider with `--provider ollama|anthropic`.

## Consequences
- Results are pessimistic and free to run. Baseline attack success is 100%, so every stopped attack is credited to a guardrail.
- Mock results say nothing about any real model's behaviour or answer quality. The system card states this.
