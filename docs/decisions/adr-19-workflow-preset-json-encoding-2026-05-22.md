---
title: ADR-19 — Workflow preset JSON encoding (deferred)
status: deferred
date: 2026-05-22
deferred_basis: R2/R3 audit findings 2026-05-22 (Slice 2). No active dispatch consumer requires machine-readable preset metadata yet; orchestrator continues to read markdown table at runtime.
authors: [your-harness Harness orchestrator]
related:
  - adr-15-multi-agent-skill-catalog-2026-05-20.md
  - adr-17-orchestrator-context-routing-2026-05-21.md
  - adr-18-orchestrator-runtime-guard-2026-05-21.md
---

## 1. Context

`CLAUDE.md` defines four workflow orchestration presets in a markdown table (Section "Orchestration Presets"):

| Workflow | Preset | Default agents |
|---|---|---|
| Bug fix | code-only | executor-agent, codex-final-reviewer |
| Feature | design-then-code | design skill → executor-agent → codex-final-reviewer + specialist |
| Refactor | small-loop | executor-agent + verify skill + codex-final-reviewer |
| Security audit | review-only | quality-agent + cwe-auditor + codex-final-reviewer |

R2 audit (2026-05-22, Slice 2) flagged: this table has no JSON surface. `orchestration_profile` in per-family JSON uses a 3-value enum (`standard | bounded | minimal`) that does not map to the four preset names. Dispatch logic has no machine-readable preset definition to validate against.

R3 audit (2026-05-22) re-confirmed the gap is still open.

## 2. Decision

**Defer JSON encoding of workflow presets.**

Rationale:
- The presets are advisory in main-orchestrator.md ("Preset selection is advisory, driven by the task classification result"). No verifier or dispatch component currently reads them as data.
- Encoding presets into JSON requires a schema design choice between (a) adding a new top-level catalog section `workflow_presets`, (b) extending `orchestration_profile` enum to seven values, or (c) embedding presets in per-family JSON. All three carry migration cost across 17 family JSONs.
- The four current presets are stable but the agent set per preset is mutable as the fleet matures (e.g., `cwe-auditor` may become a default for "feature" workflows). Premature schema encoding would lock in transient choices.

## 3. Trigger conditions to revisit

Revisit and write a follow-up ADR when ANY of the following becomes true:

1. **Dispatch consumer requires it**: a verifier, hook, or orchestrator subprocess needs to read the preset → agent_set mapping from JSON to enforce or validate dispatch.
2. **Preset drift incident**: CLAUDE.md and main-orchestrator.md disagree on a preset's agent set, and the disagreement was not caught by review.
3. **Per-family preset override needed**: a family genuinely requires a preset with a non-default agent set (e.g., <example-family> wanting `story-chapter` preset). At that point, encoding becomes a usability requirement, not just a schema cleanup.

## 4. Interim measures (in effect)

Until revisited:
- `CLAUDE.md` "Orchestration Presets" table is the SSOT.
- main-orchestrator.md MUST reference the same table in its dispatch flow.
- A `fleet-doc-steward` review during monthly cadence (ADR-15 §S5) should spot-check the two surfaces for drift.

## 5. Non-decision

This ADR does not:
- Forbid future encoding. The decision is timing, not principle.
- Add any verifier check today. The markdown table remains advisory.
- Modify any existing schema field.

## 6. Cross-references

- R2/R3 audit findings: see `tasks/review-rounds.json` round entries for `local-fleet-audit-2026-05-22`.
- Schema deferral pattern precedent: per-family `execution_backend` (ADR-20).
