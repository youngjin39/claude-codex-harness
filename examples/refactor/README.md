# Example — refactor without changing behavior

A refactor is a change that should leave the externally observable behavior identical. The risk: agents like to "improve" things during a refactor and quietly change semantics.

> **Refactor**: extract the duplicated retry logic in `client.py` and `worker.py` into a shared `retry.py` module.

## Walk-through

### 1. Establish behavior baseline first

Before any refactor, the existing tests must pass. If they do not, fix that first — the refactor cannot be evaluated against a broken baseline.

```bash
$ pytest -q
58 passed in 2.3s
```

Capture the *exact* test list. Add it to your plan as the proof.

### 2. Plan (skill: `writing-plans`)

```
Step 1 — extract the retry helper as a no-op move
  files: src/retry.py (NEW), src/client.py, src/worker.py, tests/test_retry.py (NEW)
  commands:
    - pytest -q
  expected:
    - 58 passed → 58 passed (zero behavior change)
    - 2 new tests in test_retry.py exercise the extracted helper directly

Step 2 — replace the inline retry block in client.py with a call to retry()
  files: src/client.py
  commands:
    - pytest -q tests/test_client.py
    - pytest -q
  expected:
    - test_client.py still 14 passed (no behavior change)
    - full suite still 58 passed

Step 3 — replace the inline retry block in worker.py with a call to retry()
  files: src/worker.py
  commands:
    - pytest -q tests/test_worker.py
    - pytest -q
  expected:
    - test_worker.py still 9 passed
    - full suite still 58 passed

Step 4 — verify no public API surface changed
  files: (none)
  commands:
    - python -c "import client; print(sorted(dir(client)))"
    - diff <(git show HEAD~3:client_dir.txt) <(python -c '...' )
  expected:
    - dir(client) unchanged
```

### 3. Ledger entry

The category that matters most for refactors is `compatibility` (no API change). Make it explicit.

```jsonc
{
  "id": "extract-retry-helper-2026-05-11",
  "scope": "Extract duplicated retry logic from client.py and worker.py into src/retry.py. Behavior preserving — every existing test must pass unchanged. No public surface change.",
  "targets": ["src/retry.py", "src/client.py", "src/worker.py", "tests/test_retry.py"],
  "categories": {
    "unit": {
      "status": "planned",
      "command": "pytest -q tests/test_retry.py tests/test_client.py tests/test_worker.py",
      "notes": "23 existing + 2 new direct-helper tests"
    },
    "integration": {
      "status": "covered_existing",
      "notes": "existing client/worker integration tests cover the retry path; no new tests needed"
    },
    "e2e": { "status": "covered_existing", "notes": "no entry point change" },
    "browser": { "status": "not_applicable", "reason": "no UI" },
    "edge": {
      "status": "covered_existing",
      "notes": "retry exhaustion + transient failure cases already in test_client.py and test_worker.py"
    },
    "architecture": {
      "status": "planned",
      "command": "pytest -q tests/test_imports.py",
      "notes": "client.py and worker.py both import from src/retry, no circular import"
    },
    "availability": {
      "status": "covered_existing",
      "notes": "retry-on-5xx tests in test_client.py exercise the failure modes"
    },
    "load": { "status": "not_applicable", "reason": "no perf-sensitive change" },
    "soak": { "status": "not_applicable", "reason": "no resource lifecycle change" },
    "security": { "status": "covered_existing", "notes": "no auth/secret surface touched" },
    "compatibility": {
      "status": "planned",
      "command": "python -c 'import client, worker; from inspect import getmembers; assert dict(getmembers(client)) == BASELINE'",
      "notes": "snapshot of public API before/after; must be byte-equal"
    },
    "transaction_locking": { "status": "not_applicable", "reason": "no concurrent state change" }
  }
}
```

The `compatibility` row is the heart of a refactor. It is what distinguishes "refactor" from "I rewrote it and called it a refactor".

### 4. Implement (one-step-at-a-time)

The plan deliberately splits the move from the call-site changes. After Step 1, `retry()` exists but is not used yet. Run the suite — must still be 58 passed. After Step 2, `client.py` uses it. After Step 3, `worker.py` does too.

If the suite breaks at any of those checkpoints, the refactor introduced a behavior change. Roll back the offending commit and look harder.

### 5. Review (skill: `code-review`)

Adversarial reviewer reads the diff. The most useful finding for a refactor is "the extracted code is *not* identical to the original":

```
[HIGH] src/retry.py:34 — extracted retry uses range(max_retries) but worker.py original used
                         range(max_retries + 1). Off-by-one — worker now does one fewer retry
                         than before. Fix or document the change.
[MEDIUM] src/retry.py:50 — extracted code drops the `last_exception = e` assignment that was
                           in worker.py; if the helper raises, the caller sees a generic
                           RuntimeError instead of the wrapped original. Preserve.
[LOW]   src/retry.py:1 — module docstring describes only the client use case; mention worker
                          and the shared contract.
```

The HIGH and MEDIUM are real bugs the refactor introduced. They have to be fixed before this can be called behavior-preserving.

### 6. Verify (skill: `verification`)

```
## Static
- tests: 60 passed (58 baseline + 2 new test_retry tests), 0 skipped
- lint: PASS
- type-check: PASS

## Compatibility (the critical row for a refactor)
- python -c "import client; ..." → public API byte-equal to baseline ✅
- python -c "import worker; ..." → public API byte-equal to baseline ✅
- existing integration tests → all 58 still pass ✅

## Findings
- HIGH and MEDIUM addressed (off-by-one + last_exception)
- LOW addressed (docstring expanded)

## Verdict
PASS — refactor preserves behavior. 1 net commit (after fixes), zero regression.
```

## What this example shows

- A refactor's gate is `compatibility`, not `unit`. The 12-category ledger forces you to declare that explicitly.
- One-step-at-a-time refactors catch behavior drift early. Big-bang refactors hide bugs.
- The reviewer's job on a refactor is to find the *introduced* differences, not to admire the cleaner code.
