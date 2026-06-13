---
adr: 53
status: accepted
source: mirrored-summary
---

# ADR-53 — Context-Assembly: Current-Only Core and On-Demand Retrieval

## Context

The public template needs a stable reference record for ADR-53 so applied-state verification can confirm the baseline catalog is complete.

## Decision

ADR-53 redesigns context assembly so session start carries only current, active, status-filtered information, while historical or archived content enters context only through an explicit on-demand retrieval surface. The template preserves a concise, English-only reference stub for this ADR number. Detailed execution history remains in the mir-harness control repository.

## Consequences

- The template keeps a stable ADR number map.
- Public consumers can verify baseline completeness.
- Repository-specific operational detail stays in mir-harness.
