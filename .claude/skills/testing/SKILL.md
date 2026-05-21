---
name: testing
description: "Test writing and execution.\n\nTrigger: test, TDD, unit test, integration test"
context: fork
---

# Testing

## Procedure
1. Detect test framework (package.json scripts, config files).
2. Create or update `tasks/tdd.json` before implementation edits.
3. Use Codex as the default TDD execution lane for code changes. Any non-Codex override must be explicitly recorded with reason.
4. For each changed implementation target, classify every mandatory TDD category:
   - `unit`
   - `integration`
   - `e2e`
   - `browser`
   - `edge`
   - `architecture`
   - `availability`
   - `load`
   - `soak`
   - `security`
   - `compatibility`
   - `transaction_locking`
5. Check if tests already exist for changed files. Create or extend them when coverage is missing.
6. Follow existing test patterns. Add edge cases and system-boundary checks.
7. Run the commands declared in `tasks/tdd.json`. On failure: root cause analysis → fix → re-run.

## Rules
- Test names: `should_return_X_when_Y`.
- Edge cases: null, empty, boundary, error, concurrent.
- No mocks for external services unless explicitly approved.
- Code review is not proof of correctness. Executed TDD evidence is.
- `planned` TDD categories are allowed before editing implementation code, but must not survive to commit time.
- `not_applicable` requires a concrete reason.
- `pass` and `covered_existing` require runnable commands.
- Browser and E2E categories are mandatory to classify even when they do not apply.

## GUI Testing (Computer Use)
When the project has GUI components and computer-use MCP is enabled:
1. Build and launch the app.
2. Execute UI flows: tap, scroll, navigate between screens.
3. Screenshot any visual anomalies or errors.
4. Report layout issues with screenshot evidence.

Ref: `docs/integrations/computer-use-gui-testing.md`

## Output
```
## Test Results
| File | Tests | Pass | Fail | Coverage |
|---|---|---|---|---|
| {file} | {N} | {N} | {N} | {%} |

### Failures (if any)
- {test_name}: {root cause} → {fix applied}
```
