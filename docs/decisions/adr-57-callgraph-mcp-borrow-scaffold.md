---
adr: 57
status: accepted
source: mirrored-summary
---

# ADR-57 — Code Call-Graph MCP Tool (opt-in scaffold)

## Context

The public template needs a stable reference record for ADR-57 so applied-state
verification can confirm the baseline catalog is complete.

## Decision

An opt-in, default-OFF code call-graph MCP capability (caller/callee/impact queries
over Python source, stored in the per-repo SQLite store) is borrowed in design from
the external codegraph project and reimplemented in the harness Python stack. It
ships as an implementation-deferred scaffold: the storage contract and MCP tool
surface are defined; the extractor/resolver logic lands with the first real big-code
task. The template preserves a concise, English-only reference stub for this ADR
number; detailed execution history remains in the upstream control repository.

## Consequences

- The template keeps a stable ADR number map.
- Public consumers can verify baseline completeness.
- The capability is opt-in and default-OFF, preserving baseline context discipline;
  activation is per-repo and gated on real big-code need.
