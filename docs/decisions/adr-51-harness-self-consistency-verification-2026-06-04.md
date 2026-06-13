---
adr: 51
status: accepted
source: mirrored-summary
---

# ADR-51 — Harness Self-Consistency Verification

## Context

The public template needs a stable reference record for ADR-51 so applied-state verification can confirm the baseline catalog is complete.

## Decision

ADR-51 introduces a reusable, deterministic harness self-consistency verifier that detects structural drift (dead hooks, stale references, status-versus-reality mismatches) that a passing test suite would otherwise hide. The template preserves a concise, English-only reference stub for this ADR number. Detailed execution history remains in the mir-harness control repository.

## Consequences

- The template keeps a stable ADR number map.
- Public consumers can verify baseline completeness.
- Repository-specific operational detail stays in mir-harness.
