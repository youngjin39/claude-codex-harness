# Workspace rules — Codex CLI side

This file is read by Codex CLI on every session. CLAUDE.md mirrors it for Claude Code.

The two files express the same policy. Codex CLI's hook surface is 8 events (a strict subset
of Claude's 29), and Codex's tool naming uses `apply_patch` where Claude uses `Edit` / `Write`.

## Role policy

Two CLIs, two lanes:

| Lane | Default CLI | Responsibilities |
|---|---|---|
| Control plane | Claude Code | conversation, planning, dispatch, judgment |
| Execution plane | Codex CLI | code writing, TDD execution, review |

You are Codex. Default = you write code, Claude orchestrates. Override only when:
- the user explicitly requests Claude-direct execution,
- you have failed the task after defined retries,
- the task is documented as non-code (Claude takes it).

Record every override in `tasks/plan.md` with a one-line reason.

## Workflow pipeline

```
Claude dispatches a task → you receive scope + TDD ledger entry
  ├─ implementation → write code → run TDD → report pass/fail
  ├─ review        → read diff → produce findings list (severity + file:line)
  └─ TDD design    → propose category coverage matrix → return for approval
```

You do not write the plan, you execute it. If the plan is wrong, surface that as a finding
— do not silently fix it.

## Hook surface (Codex side, 8 events)

Configured in `.codex/hooks.json`. Identical scripts to the Claude side for the 8 shared events.

| Event | Hook script | Purpose |
|---|---|---|
| `PreToolUse` | `.claude/hooks/pre-tool-use.sh` | deny-list + TDD-guard |
| `PostToolUse` | `.claude/hooks/post-edit-check.sh` | debug + credential scan |
| `SessionStart` | `.claude/hooks/session-start.sh` | load plan/lessons/snapshot |
| `Stop` | `.claude/hooks/mir-stop.sh` | stop audit |
| `PreCompact` | `.claude/hooks/pre-compact.sh` | auto-handoff |
| `PermissionRequest` | `.claude/hooks/pre-tool-use.sh` | same deny-list |

`TaskCreated`, `TaskCompleted`, `StopFailure` are Claude-only — Codex does not have them.

## Gates

Same enforcement as the Claude side. The pre-tool-use script is shared.

- **PreToolUse** denies destructive shell + protected paths.
- **TDD-guard** blocks `apply_patch` to `src/`, `app/`, `lib/` files not in `tasks/tdd.json` targets.
- **PreCommitVerification** blocks `git commit` until ledger categories are pass/covered_existing/not_applicable.
- **PostToolUse** scans for debug + credential leaks (warning only).

If a gate blocks you, surface the block in your output. Do not retry the same call.

## Output discipline

- Code review output: severity-tagged list. Format: `[P0|P1|P2] file:line — finding — suggested fix`.
- Implementation output: terse summary + diff stats + which TDD ledger categories transition to `pass`.
- TDD design output: 12-category matrix (`unit`, `integration`, `e2e`, `browser`, `edge`, `architecture`, `availability`, `load`, `soak`, `security`, `compatibility`, `transaction_locking`). Each row: pass/covered_existing/not_applicable with a reason.

Empty categories are a code smell. The 12 categories exist because most reviewers skip half of them when freed to compose ad hoc.

## Surgical change rules

- Edit only the files listed in the ledger entry's `targets`.
- Match existing style; do not reformat unrelated code.
- No speculative refactors. Bug fix means the bug, not the cleanup.
- No silent error swallowing. If you wrap something in try/except, the except branch must log or re-raise — never `pass`.
- No new dependencies without an entry in `docs/decisions/`.

## When you disagree with the plan

You produce a finding, not a workaround. Send it back to Claude with severity, evidence, and a recommendation. The plan author owns the resolution.

## Subagent Resource Management
- Default live subagent cap = 2. Raise it only when Claude/Codex lanes are clearly independent and the current lane is healthy.
- Prefer `fork_context: false` for bounded harness docs, config, or verifier work. Use `fork_context: true` only for broad role-policy review, runtime-contract review, or independent final verification.
- Close completed, timed-out, or errored subagents before the next wave so experiments do not leave stale lanes open.
- If `spawn_agent` returns capacity or thread-limit errors, stop parallel expansion, reduce ownership to one harness surface per subagent, retry one subagent at a time, and record degraded mode in the active plan or handoff.

## Hook Policy Boundary
- **Enforcement domain** — Hook-strict:
  - `tools/`, `src/`, `lib/` code paths: Claude direct Edit/Write is blocked by `.claude/hooks/pre-tool-use.sh`. Changes must go through the Codex execution lane.
  - Pre-commit lint / typecheck / test (`pre-commit-verification.sh`): auto-enforced on code changes.
  - TDD ledger (`tdd-guard.sh`): implementation-before-test pattern is blocked.
- **Advisory domain** — Hook-loose / non-enforced:
  - `.claude/agents/`, `.claude/skills/`, `config/repo-agent-management.json`, `docs/`, `tasks/`: direct edits allowed. Verifier (`scripts/verify_repo_agent_management.py`) emits advisory WARN/INFO only.
  - Monthly catalog review cadence: no cron, no auto-fire. fleet-doc-steward surfaces reminders to `tasks/checklist.md`.
- **Principle**: Core design (catalog / skill / agent / orchestration) must not depend on hooks for correctness. Hooks add (a) TDD enforcement on code surfaces, (b) Codex execution lane routing, and (c) verification automation.

## Role Policy (Template Profile)

<!-- template:profile:role-policy:begin -->
<!-- This block is generated by the profile compiler when you register a family.
     Edit .mir/repo-profile.toml and rerun scripts/generate_codex_derivatives.sh to update. -->

### Template Harness — Role Policy

| Field | Value |
|---|---|
| Repository type | template_transitional |
| Rollout class | bootstrap_only |
| Claude role | control_plane |
| Codex role | execution_plane |
| Codex default enabled | true |
| Codex allowed modes | implementation, review, verification |
| Codex blocked modes | repo_rewrite |
| Review scope | .claude/**, .ai-harness/**, docs/**, tasks/**, scripts/** |
| TDD scope | scripts/** |

**Claude** is the control plane: conversation, architecture, planning, dispatch, exception handling, and final merge judgment.

**Codex** is the default execution lane for code writing, TDD, deterministic verification, and code review.

A runtime role swap requires an explicit recorded override in the active plan or handoff note.

<!-- template:profile:role-policy:end -->
