---
adr: 55
status: accepted
source: mirrored-summary
---

# ADR-55 — Native Agent-Home Memory as a DB Projection

## Context

The public template needs a stable reference record for ADR-55 so applied-state verification can confirm the baseline catalog is complete.

## Decision

ADR-55 makes native agent-home memory a database projection: the markdown files remain on disk but are sourced from a database render and reconciled, closing the dual-write drift that ADR-50 left open. The template preserves a concise, English-only reference stub for this ADR number. Detailed execution history remains in the mir-harness control repository.

## Consequences

- The template keeps a stable ADR number map.
- Public consumers can verify baseline completeness.
- Repository-specific operational detail stays in mir-harness.
