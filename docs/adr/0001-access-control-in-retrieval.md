# ADR-0001: Enforce document access control in the retriever, not the prompt

**Status:** Accepted

## Context
A common RAG pattern retrieves everything and tells the model "do not reveal confidential documents to unauthorised users". That control lasts only until the first successful prompt injection.

## Decision
Each chunk carries a classification label. The retriever drops chunks above the caller's clearance **before** ranking, so they never enter the prompt.

## Consequences
- Access control holds even if the model is fully compromised (AC-01 to AC-04 are stopped with no help from the model).
- Labels must be correct at ingest. Mislabelling is now the main risk, so corpus changes go through review.
- Per-user filtering stops a shared answer cache from being used safely across roles.
