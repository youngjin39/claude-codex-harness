---
name: git-commit
description: Commit hygiene rules. Subject + body format, safety rules, structured trailers.
trigger: commit, git, save changes
---

# git-commit

Loaded when the user asks to commit changes. The skill exists because agent-generated commits are often noise — vague subjects, missing context, accidental scope creep.

## Subject line

- 50 chars or fewer when possible, hard cap at 72.
- Imperative mood: "add", "fix", "update" — not "added", "fixes", "updating".
- Type prefix when the project uses one: `feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`, `ci:`.
- No trailing period.

Good: `fix(cli): handle CJK output on non-utf8 stdout`
Bad: `fixes some bugs in the cli tool I think`

## Body

- One blank line after the subject.
- Wrap at 72 chars per line.
- Explain *why*, not *what* (the diff already shows the what).
- Reference related work: ledger entry id, issue number, design doc.
- If the commit is the result of a multi-round review, name the round and the finding count.

## Safety rules

These are baked into the harness; the skill restates them so the agent does not propose violating them.

1. **Never** force-push to `main` / `master`. The deny-list pattern blocks it.
2. **Never** add `--no-verify`. The deny-list blocks it.
3. **Never** commit secrets, even fake-looking ones. The post-edit-check warns; the agent should clean before staging.
4. **Never** amend a commit that is already pushed. Create a new one.
5. **Never** stage everything with `git add -A` when only a subset is yours. Stage by name.

## Trailers

For tools that read commit trailers (changelog generators, CI), include them at the bottom.

- `Co-Authored-By: <name> <email>` for pair work.
- `Refs: #123` for issue links.
- `Reviewed-by: <name>` for explicit review attribution.

The harness's own `Co-Authored-By: Claude` trailer (or equivalent for Codex) is added automatically by the dispatching agent — do not double-add.

## Single-commit principle

One commit, one logical change. If you find yourself writing two paragraphs in the body each describing a different change, split the commit. The pre-commit hook does not enforce single-purpose, but reviewers will.

## When the commit fails

- Pre-commit hook blocks → read the message, fix the underlying issue, then re-commit. Never bypass.
- Commit-message lint fails → rewrite the message, then re-commit (use `git commit --amend` only on un-pushed commits).
- Conflicting paths → resolve, do not delete. The harness assumes you understand the conflict before committing.

## Anti-patterns

- "fix bug" — too vague.
- "WIP" — never on `main`. If the commit is in progress, it stays on a branch.
- "Updated 5 files" — describe the change, not the delta.
- Subject that mentions the developer ("yj's changes") — commits are not authored by the subject line.
