---
name: code-review
description: "Code review and quality check.\n\nTrigger: code review, PR, quality, merge check, post-completion\n\nNote: \"architecture review\" routes to bluebricks (not this skill); use the compound trigger \"code review\" to disambiguate."
context: fork
allowed-tools: Read, Grep, Glob, Bash
---

# Code Review

## Default Review Policy
- Primary code review lane: Codex.
- Primary correctness gate: executed composite TDD evidence.
- Claude-side `quality-agent` review is fallback or secondary synthesis, not the default reviewer for code changes.
- If review runs anywhere other than Codex, record the override reason in `tasks/plan.md` or the active handoff note.

## Procedure
1. Identify changed files (`change_log.md` or `git diff`).
2. Determine **source scope** before reviewing — read the *Scope SSOT* (see §5b) and pin the boundary.
3. Run Codex review on the diff by default.
4. Per file: error handling gaps, security risks, naming violations, duplication, unnecessary complexity.
5. Classify each finding: **P0 (CRITICAL — model-shaking)** / **P1 (HIGH)** / **P2 (LOW)**.
6. For every P0 finding produce **≥1 alternative candidate** (see §Defect + Alternative Mode).
7. Apply **scope filter (§5b)** + **citation verification (§5a, runs in `verification` skill stage 0)** before recording verdict.
8. Structured report with evidence (cite exact lines).

## Round Counter + Reroll ASK (ADR-07 Phase 7E)

Each merge attempt is a **round** for the active PR. The L2 hook (`pre-merge-gate.sh` step 6) is the **single source of truth for round increments** — SKILL.md must NOT call `increment` itself (review W5: double-increment risk if both SKILL.md and hook increment per merge attempt).

SKILL.md responsibilities (advisory):

- **Read** the active round state: `uv run python -m tools.review_rounds query-active --pr-ref <ref>` to see `round_number` and prior `findings[]` for cross-reference.
- **Close** the round after a verdict is reached: `close --round-id <id> --verdict <Sound|Reroll>`.
- **Defer** P2 findings at round 3+: `defer --round-id <id> --reason "round 3+ P2 deferred"`.
- **Record** findings (incl. Stage 0 citation results): `record-finding --round-id <id> --severity P0/P1/P2 ...`.

Round semantics:

- `round_number == 1`: first merge attempt (hook increments on entry to pre-merge gate; verdict assigned by reviewer + verification).
- `round_number == 2`: second merge attempt; cross-reference previous round's findings.
- `round_number >= 3`: **the L2 hook blocks the merge command deterministically** (`should-ask` exits 0). Treat this round as P0/P1-only — P2 findings are recorded but flagged `deferred` and removed from verdict input. Surface a Discord ASK to the user with three options:
  ```
  Round 3+ reached for {pr-ref}. Choose:
  1. Reroll — restart from §1 design step (resets round counter via close + new local-* ref)
  2. Sound  — accept current verdict, close the round, retry merge
  3. Ignore — defer round; user takes responsibility
  ```
- After user reply: invoke `close --verdict Sound` or `close --verdict Reroll` (or `defer --reason ...`) on the round_id.

Hook-level enforcement: `should-ask --pr-ref <ref>` exits 0 when `round_number >= 3` for any **open** round of that pr_ref, which `pre-merge-gate.sh` translates to `exit 2 = block` plus Discord notification. SKILL.md body remains advisory — the deterministic brake lives in the L2 hook.

## §5a Reviewer Citation Verification

Delegated to `verification` skill (`Stage 0` of the 7-stage gate). Every reviewer finding that cites a file:line must be Read by the main orchestrator and confirmed verbatim before the finding enters the verdict input. Findings whose citation fails verification are stamped `scope_status="false-positive"` and recorded in `review-rounds.findings[].citation_verified=false`.

## §5b Scope Filter

**Scope SSOT** (read once before review starts):

1. `tasks/plan.md` current phase scope row (preferred when an active phase is in progress).
2. The active ADR's `§1 Context` or `§2 Decision` section (when no plan row matches).
3. The user-pinned scope of the active handoff note (`tasks/handoffs/*.md`).

Each finding's prescription must fall inside the scope. Out-of-scope prescriptions retain their severity but receive one of these execution paths:

| `scope_status` | meaning |
|---|---|
| `fix-now` | inside scope; apply in this round |
| `reroute` | outside scope; redirect to the responsible domain (annotate next steps) |
| `escalate` | inside scope but outside the reviewer's domain expertise — surface for orchestrator decision |
| `user-confirm` | within scope but touches user-pinned boundary — request explicit user decision |
| `false-positive` | citation failed §5a, or pattern misread; remove from verdict input |

Record each finding's `scope_status` via `record-finding --scope-status ...`.

## Defect + Alternative Mode

Every P0 (and at least one P1 per file when reviewing > 5 P1s) carries:

- **≥1 alternative candidate**: a specific other approach to fix the same defect.
- **Recommendation (one line)**: which candidate the reviewer endorses + a one-line reason.

**Trivial candidate ban** (rejected as "no alternative"):
- "do nothing" / "keep current design" / "leave as TODO" / "later"
- Empty placeholders such as "consider X" without committing to a direction.

If no real alternative exists, write `No alternative — <one-line reason>`. A bare `No alternative` with no reason fails the output contract.

## Trivial Pass Track 1 (docs/typo only)

Multi-reviewer dispatch can be skipped iff **all** of the following hold:

- Diff ≤ 10 lines.
- No code-extension files in the diff (`.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.rs`, `.go`, `.rb`, `.java`, `.kt`, `.swift`, `.c`, `.cc`, `.cpp`, `.h`, `.hpp`, `.sql`). **The `pre-merge-gate.sh` Step 5 path-gate prints an INFO line when this condition is violated; LLM self-claim of "trivial" for a code-touching diff fails the SKILL contract** (review Skill W4 — advisory + hook-assisted enforcement).
- No changes to: `instructions/core/`, `AGENTS.md`, `CLAUDE.md`, `.ai-harness/*.md`, `config/*.yaml`, `tools/profile_compiler/`, `.claude/hooks/`, `.claude/skills/`, `tasks/phase.json`, `tasks/tdd.json`, `tasks/review-rounds.json`, schema files.
- Regression risk = 0 (no behavior change reachable via the diff).

When Track 1 fires: state explicitly `"Trivial Pass Track 1 — docs/typo only, multi-reviewer skipped"` in the verdict and proceed straight to `Sound`. Ambiguous = not trivial.

Track 2 (workflow body / skill body) is **not supported** in this harness; the substrate (`workflows/llm_driven/` or `skills/library/`) that upstream review-gate.md (v2.9.23) defines that track over is not present here.

## Checklist
- [ ] Error handling (missing try/catch, unhandled promises)
- [ ] Security (injection, auth, credential exposure)
- [ ] Naming conventions (consistent with project)
- [ ] No duplication (DRY violations)
- [ ] No over-engineering (YAGNI violations)
- [ ] Each P0 has ≥1 alternative candidate (Defect + Alternative mode)
- [ ] Each finding has `scope_status` assigned (§5b)
- [ ] Citation verified for every cited file:line (§5a via verification stage 0)

## Output Contract (7-column)

```
## Code Review — round {N} ({pr_ref})

| File:Line | Severity | Finding | Evidence | scope_status | Alternatives | Recommendation |
|---|---|---|---|---|---|---|
| {file}:{line} | P0/P1/P2 | {issue} | {snippet} | fix-now/reroute/escalate/user-confirm/false-positive | A) ... B) ... | A — {1-line reason} |

### Summary
- P0: {N}
- P1: {N}
- P2: {N}
- Excluded (false-positive / scope=reroute): {N}

### Verdict (input to §5d)
Sound / Reroll  ← reviewer's signal; orchestrator finalises after §5a/§5b/§5c
```

## External Review
When GitHub + Codex review is configured:
1. Treat Codex PR review as the default external second pass, not an optional nice-to-have for important code changes.
2. After Codex review comments arrive, address all actionable findings before merge.
3. Escalate unresolved disagreement to Claude orchestration or the user.

Ref: `docs/integrations/codex-code-review.md`

## Banned phrases (advisory contract — `feedback_enforcement_is_code` align)
- "looks good" / "should be fine" / "probably OK"
- Recommending without an alternative (Defect + Alternative mode violation)
- Marking a P0 alternative as "TODO" / "consider X" / "do nothing"

## Related skills
- `verification` — Stage 0 citation check (§5a) + 6-stage gate
- `brainstorming` — design-phase gate (before code, comparable Banned Patterns)
- `runner` — long-running review dispatch (if review needs background execution)

## ADR References
- `docs/decisions/adr-07-review-gate-2026-05-11.md` (this skill's L1 surface contract)
- `tasks/handoffs/adr-07-writing-plans-2026-05-11.md` (Phase 7C concrete output examples)
