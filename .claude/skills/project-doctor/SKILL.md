---
name: project-doctor
description: Health check. Walks the harness state and reports drift, missing pieces, dirty work-tree.
trigger: diagnose, doctor, health check, status
---

# project-doctor

Loaded when the user asks to "check on the project" or "what's the state". The skill produces a single-page report with severity-tagged observations.

## Checks

### Repository hygiene

- `git status --short` — anything uncommitted?
- `git diff --check` — whitespace issues?
- Branches that have been merged but not deleted.
- Tags that point at non-existent commits.

### Harness state

- Does `.claude/settings.json` exist and parse as JSON?
- Does `.codex/hooks.json` exist and parse as JSON?
- Are all `.claude/hooks/*.sh` executable?
- Does `.ai-harness/deny-list.yaml` parse correctly?
- Does `tasks/tdd.json` parse and have the expected schema?

### Working ledger

- Is there an in-progress phase in `tasks/plan.md`? How long has it been in progress?
- Are there ledger entries with `planned` status that should have been closed?
- Is `tasks/lessons.md` growing (sign of healthy retrospective) or static (sign of skipped closeouts)?
- Are there session snapshots older than 30 days that should be archived?

### Memory layer

- Does `docs/memory-map.md` index all the docs/ files actually present?
- Are there docs/ files referenced in the index that have been deleted?
- Are there decisions referenced in `tasks/plan.md` that do not have an ADR file?

### Tests + lint

- Run the project's test command (read from CLAUDE.md / package.json / pyproject.toml).
- Run the project's lint command.
- Report counts and failures.

## Output format

```
## Repository
✅ working tree clean
✅ no whitespace issues
⚠️  4 stale local branches: feature-X (90 days old), ...

## Harness state
✅ .claude/settings.json valid
✅ .codex/hooks.json valid
✅ all hook scripts executable
❌ .ai-harness/deny-list.yaml has invalid yaml at line 23

## Ledger
✅ tasks/tdd.json schema valid
⚠️  ledger entry 'add-cache-2026-04-15' has been in `planned` status for 26 days
⚠️  3 entries reference src/foo.py which no longer exists

## Memory
✅ docs/memory-map.md indexes 12 files, all present
❌ docs/memory-map.md references docs/decisions/adr-04.md which is missing

## Tests
✅ pytest -q → 142 passed, 1 skipped (1.8s)
✅ ruff check → clean

## Verdict
⚠️ 2 issues need attention (deny-list yaml + missing ADR)
```

## What this skill does NOT do

- Fix anything. It only reports.
- Decide priority. The user picks what to address first.
- Run integration tests that take more than 30 seconds. Use a separate skill for slow checks.

## When to run

- Start of a session if `tasks/plan.md` says the previous session ended unclean.
- After a long break from the project (>2 weeks).
- Before a release or a large refactor.
- Whenever you have the suspicion that the project state is drifted.

## Cost expectation

A clean project doctor run takes <30 seconds. If yours takes longer, the project has accumulated cruft and the doctor's job is now to flag it.
