# ADR-18 — Orchestrator runtime guard (sanitized summary)

Status: accepted (upstream)

Sanitized summary of the upstream ADR. Captures the dispatch-routing
guard contract that public-template fork users rely on.

## Decision

For every agent that declares `execution_backend: codex`, the
orchestrator MUST dispatch through the Codex CLI subprocess pattern,
not via direct Agent-tool invocation. This is enforced at two layers:

**Layer 1 — orchestrator self-check (prompt-level).** The
`main-orchestrator.md` body carries a "Codex Backend Dispatch
Self-Check" section that must be followed before any dispatch.

**Layer 2 — verifier post-hoc audit (R11).** A check in
`scripts/verify_repo_agent_management.py` scans
`tasks/log/dispatch-log.jsonl` and WARNs on entries that violate the
contract.

This is intentionally prompt-level + post-hoc rather than hook-based.
A hook-based intercept was previously cancelled for structural
defects.

## Dispatch log schema

`tasks/log/dispatch-log.jsonl` lines have shape:

```json
{
  "ts": "2026-05-21T10:30:00Z",
  "agent_slug": "codex-final-reviewer",
  "routed_via": "codex_cli",
  "purpose": "final_review",
  "task_id": "task-N",
  "note": "optional human-readable audit context"
}
```

`routed_via` enum: `codex_cli | claude_session | unknown |
skipped_inactive | skipped_empty_scope`.

- `codex_cli` — compliant.
- `claude_session` / `unknown` — violation, R11 WARN.
- `skipped_inactive` — Active Agent Resolution refused dispatch
  (specialist not in `active_agents`). R11-exempt.
- `skipped_empty_scope` — Specialist Scope-Pattern Routing produced
  an empty filtered file set. R11-exempt.

Entries with `note` containing `audit-truthful` are R11-waived
(historical pre-ADR-18 records intentionally preserved).

## Scope

All agents declaring `execution_backend: codex` regardless of
catalog `status`. Currently three agents:
- `codex-final-reviewer`
- `executor-agent`
- `pipeline-validator`

New agents added with `execution_backend: codex` enter the guard
automatically.

## See also

- `docs/decisions/adr-09-execution-backend-frontmatter.md`
- `.claude/agents/main-orchestrator.md` Codex Backend Dispatch
  Self-Check section.
- `scripts/verify_repo_agent_management.py` `_check_codex_backend_dispatch_log`.
