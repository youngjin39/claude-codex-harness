# Changelog

## 2026.05.1 — content expansion

- Expanded README comparison section into a 7-row matrix (vs Claude Code default, Codex CLI default, superpowers, Archon, OpenHarness, claude-code-skills, hand-rolled CLAUDE.md). Names the unique slice this template fills.
- Added 3 examples: `examples/fix-bug/`, `examples/refactor/`, `examples/multi-round-review/` — the last is an anonymized walkthrough of a real multi-round adversarial review that landed a 500-LOC change in 3 rounds.
- Added 3 skills: `deep-interview` (ambiguity gate), `git-commit` (commit hygiene + safety rules), `project-doctor` (health check / drift report).

## 2026.05 — initial public release

- Dual-CLI harness: Claude Code + Codex CLI, identical hook scripts on the 8 shared events.
- 5 hook scripts: `pre-tool-use`, `post-edit-check`, `session-start`, `session-end`, `pre-compact`, plus the `tdd-guard` helper.
- 5 built-in skills: `design`, `writing-plans`, `testing`, `code-review`, `verification`.
- `.ai-harness/` rule set: common rules, development rules, deny-list, TDD matrix, session closeout, failure patterns.
- `tasks/` + `docs/` working ledger.
- Worked example: `examples/add-feature/`.
