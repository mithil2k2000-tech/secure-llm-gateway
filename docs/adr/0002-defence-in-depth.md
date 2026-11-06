# ADR-0002: Treat the injection detector as one layer, not the defence

**Status:** Accepted

## Context
The author's study of lightweight prompt-injection detectors (Rebuff and Vigil heuristics, n-gram classifiers, on four public datasets) found:
- they catch few attacks outside the data they were tuned on;
- simple obfuscation such as zero-width characters, leetspeak or base64 defeats them.

## Decision
- Keep a heuristic detector, but run it on normalised text: NFKC, zero-width characters removed, base64 runs decoded, and a leetspeak variant scored too.
- Design every other control to work assuming the detector has been bypassed:
  - retrieval access control;
  - ingest quarantine;
  - spotlighting;
  - canary-based leak detection;
  - image and link removal;
  - PII redaction;
  - HTML escaping.

## Consequences
- In the evaluation, SP-03 and SP-04 get past the input filter but are caught by the canary on the way out.
- OB-05, a paraphrase, gets past every layer. Because of the other layers, all it can make the assistant say is a harmless string. It is recorded as a known gap, not hidden.
- A model-based classifier could be added as another layer later. It would not replace the others.
