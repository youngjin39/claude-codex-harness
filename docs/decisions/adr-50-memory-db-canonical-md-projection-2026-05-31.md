---
adr: 50
status: accepted
source: mirrored-summary
---

# ADR-50 — Memory DB Canonical + Markdown Projection

## Context

The public template needs a stable reference record for ADR-50 so applied-state verification can confirm the baseline catalog is complete.

## Decision

ADR-50 promotes the memory database (`.mir/memory.db`) to the single source of truth for recall and indexing; the human-readable markdown views (`memory-map.md`, `lessons.md`) become generated projections of the database rather than hand-maintained indexes. The template preserves a concise, English-only reference stub for this ADR number. Detailed execution history remains in the mir-harness control repository.

## Consequences

- The template keeps a stable ADR number map.
- Public consumers can verify baseline completeness.
- Repository-specific operational detail stays in mir-harness.
