---
adr: 54
status: accepted
source: mirrored-summary
---

# ADR-54 — Template-Anchored Fleet Parity Manifest

## Context

The public template needs a stable reference record for ADR-54 so applied-state verification can confirm the baseline catalog is complete.

## Decision

ADR-54 mechanizes template-to-repository parity as a generated manifest plus an advisory checker and a weekly read-only scan, turning the question 'is this repository in sync with the template?' into a deterministic command. The template preserves a concise, English-only reference stub for this ADR number. Detailed execution history remains in the mir-harness control repository.

## Consequences

- The template keeps a stable ADR number map.
- Public consumers can verify baseline completeness.
- Repository-specific operational detail stays in mir-harness.
