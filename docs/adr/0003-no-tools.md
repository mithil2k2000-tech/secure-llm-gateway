# ADR-0003: No tools, plugins or write actions

**Status:** Accepted

## Context
OWASP LLM06 (excessive agency) arises when a model can call tools, send messages or change data. Combined with prompt injection, that turns a wrong answer into a harmful action.

## Decision
The assistant only reads an access-filtered corpus and returns text. It has no function calling, browsing, email or database writes.

## Consequences
- The worst case for a successful injection is a misleading answer, which citations and the "check the source" notice mitigate.
- Any future tool needs a new risk assessment, least-privilege credentials scoped to the user, and human confirmation for side effects.
