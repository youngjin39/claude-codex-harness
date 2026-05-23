---
title: ADR-20 — Per-family execution_backend schema field (deferred)
status: deferred
date: 2026-05-22
deferred_basis: R1/R2/R3 audit findings 2026-05-22 (Slice 2). Per-agent execution_backend already encodes dispatch routing; per-family override is structural addition without a current consumer.
authors: [your-harness Harness orchestrator]
related:
  - adr-09-execution-backend-frontmatter-2026-05-12.md
  - adr-15-multi-agent-skill-catalog-2026-05-20.md
  - adr-18-orchestrator-runtime-guard-2026-05-21.md
---

## 1. Context

ADR-09 introduced `execution_backend: claude | codex` as agent-level frontmatter in `.claude/agents/*.md`. The catalog (`config/repo-agent-management.json` `catalog.agents.<slug>.execution_backend`) mirrors this per-agent value.

R1 audit (2026-05-22, Slice 2) flagged: per-family JSON (`config/repos/<slug>.json`) has no `execution_backend` field in the `$defs/repository` schema. The question "which families use Codex as executor" is therefore not directly machine-readable from the per-family JSON — it must be derived by joining family's active_agents list against the catalog's per-agent execution_backend values.

R2 audit (2026-05-22) re-confirmed the gap.
R3 audit (2026-05-22) re-confirmed the gap.

## 2. Decision

**Defer adding `execution_backend` to the per-family schema.**

Rationale:
- The catalog-level per-agent `execution_backend` is the existing SSOT. Per-family routing is derivable via join — no information loss.
- your-harness's role policy (CLAUDE.md "Role Policy (your-harness Profile)") declares Claude=control, Codex=execution for the meta_harness family. Per-family override would be a structural addition for the case where a family inverts this. No active fleet member has such an inversion need.
- Adding the field requires deciding semantics: is it a default for un-mapped agents? An override of catalog per-agent values? A policy assertion? Each interpretation has different schema and validator implications.
- ADR-18 §S2 dispatch self-check already enforces routing at the per-agent level via main-orchestrator and dispatch-log audit (R11). The per-family field would be redundant with this enforcement layer.

## 3. Trigger conditions to revisit

Revisit when ANY of the following becomes true:

1. **A family declares inverted role policy**: e.g., a family wants Claude=execution, Codex=control (unlikely but plausible for a Claude-skill-heavy content family). At that point the family-level field becomes a real declarative surface, not redundant metadata.
2. **Fleet-wide policy split**: if some families adopt a "Codex-only" policy (executor + reviewer both Codex) and others "Claude-only" (e.g., sealed reference repos), the per-family backend default becomes informative.
3. **Reviewer audit tool asks**: if `fleet-doc-steward` or `quality-agent` needs to surface "families with Codex execution" without joining against the catalog, the field becomes a productivity win.

## 4. Interim measures (in effect)

Until revisited:
- The catalog `catalog.agents.<slug>.execution_backend` is the SSOT for per-agent backend routing.
- Family-level "which backend does this family execute on" is answered by joining `config/repos/<slug>.active_agents` against the catalog. Tools needing this signal (e.g., `tools/agent_loader`) MUST do the join, not look for a family-level field.
- `tasks/log/dispatch-log.jsonl` per-dispatch records (ADR-18 §S2) are the runtime audit surface.

## 5. Non-decision

This ADR does not:
- Forbid future encoding. The decision is timing, not principle.
- Modify the existing per-agent `execution_backend` field or its enum.
- Add a per-family routing override mechanism.

## 6. Cross-references

- R1/R2/R3 audit findings: see `tasks/review-rounds.json` round entries for `local-fleet-audit-2026-05-22`.
- Schema deferral pattern precedent: workflow preset JSON encoding (ADR-19).
