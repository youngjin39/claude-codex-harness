# Example — fix a bug end-to-end

A bug-fix workflow that lands the regression test before the fix, and uses the harness gates as the safety net.

> **Bug report**: `mytool --reverse "hello"` outputs `<unprintable>`. Expected `"olleh"`.

## Walk-through

### 1. Reproduce first (skill: none — just shell)

Before any code change, reproduce the bug. Reproduction is the spec for the regression test.

```bash
$ python -m mytool --reverse hello
<unprintable>
```

Capture the exact reproduction. Anything you cannot reproduce, you cannot prove fixed.

### 2. Quick triage (skill: `deep-interview` — when ambiguous)

The reporter described the failure but not the cause. Two hypotheses:

- **H1**: `--reverse` operates on bytes instead of code points; the CJK characters get split.
- **H2**: `--reverse` calls `print()` without `flush=True` in a buffer-broken environment.

Triage: replicate locally with output redirected to a file. If the bytes are wrong → H1. If the bytes are right but terminal showed garbage → H2.

```bash
$ python -m mytool --reverse hello | xxd | head
00000000: ec 96 b4 ea b5 ad ed 95 9c 0a
```

These are valid UTF-8 for `olleh` plus newline. So H2 — terminal/locale issue. But that means the function is correct; the visible failure was an environment issue. **Mark this finding and ask the user**: is the goal to make the function robust to locale, or should the user fix their terminal?

If the user says "make the function robust", continue. Otherwise close as not-a-bug.

### 3. Plan (skill: `writing-plans`)

Assume user said "make robust". Plan:

```
Step 1 — write the regression test
  files: tests/test_cli.py
  commands:
    - pytest -q tests/test_cli.py::test_reverse_cjk
  expected:
    - test FAILS (because we have not fixed the bug yet)

Step 2 — add explicit utf-8 stdout encoding to the CLI entry
  files: src/cli.py
  commands:
    - pytest -q tests/test_cli.py::test_reverse_cjk
    - python -m mytool --reverse hello
  expected:
    - test passes
    - stdout shows 'olleh' on terminals with utf-8 locale, falls back gracefully on others

Step 3 — verify regression
  files: (none)
  commands:
    - pytest -q
    - ruff check src/ tests/
  expected:
    - full suite green
    - lint clean
```

### 4. Ledger entry

```jsonc
{
  "id": "fix-cjk-reverse-output-2026-05-11",
  "scope": "Make `mytool --reverse` robust to non-UTF-8 stdout locales by forcing UTF-8 encoding at the CLI entry point. Adds a regression test that exercises CJK characters end-to-end.",
  "targets": ["src/cli.py", "tests/test_cli.py"],
  "categories": {
    "unit": { "status": "planned", "command": "pytest -q tests/test_cli.py::test_reverse_cjk", "notes": "exercises CJK + ASCII mixed input" },
    "integration": { "status": "covered_existing", "notes": "tests/test_cli_integration.py already exercises CLI entry" },
    "e2e": { "status": "planned", "command": "PYTHONIOENCODING= python -m mytool --reverse hello", "notes": "stdout=olleh even when PYTHONIOENCODING is unset" },
    "browser": { "status": "not_applicable", "reason": "CLI tool" },
    "edge": { "status": "planned", "command": "pytest -q tests/test_cli.py -k reverse_edge", "notes": "empty + emoji + RTL + 4-byte UTF-8" },
    "architecture": { "status": "covered_existing", "notes": "no module boundary touched" },
    "availability": { "status": "not_applicable", "reason": "no retry surface" },
    "load": { "status": "not_applicable", "reason": "not on hot path" },
    "soak": { "status": "not_applicable", "reason": "no long-running resource" },
    "security": { "status": "not_applicable", "reason": "no boundary touched" },
    "compatibility": {
      "status": "planned",
      "command": "python -c 'import sys; assert sys.stdout.encoding'",
      "notes": "Python 3.7+ assumed; fallback works on 3.7"
    },
    "transaction_locking": { "status": "not_applicable", "reason": "single-writer CLI" }
  }
}
```

### 5. Implement (test first)

Step 1: write the regression test. The TDD-guard hook lets `tests/test_cli.py` through (the entry's `targets` lists it). Test fails locally. That is the spec.

Step 2: edit `src/cli.py`. Hook lets it through. Run the test → passes.

### 6. Review (skill: `code-review`)

The reviewer reads the diff, produces:

```
[MEDIUM] src/cli.py:23 — sys.stdout.reconfigure(encoding="utf-8") is Python 3.7+; doc the
                         floor in CHANGELOG.md or add a runtime check.
[LOW]    tests/test_cli.py:48 — test name says "cjk" but covers Korean only; add a Japanese
                                or Chinese case to make the name truthful.
```

The planner decides: roll the LOW into this PR (one extra assertion), defer the MEDIUM to a follow-up issue.

### 7. Verify (skill: `verification`)

Closeout:

```
## Static
- tests: 32 passed (4 new), 0 skipped, 1.4s
- lint: PASS
- type-check: PASS

## E2E
- python -m mytool --reverse hello → 'olleh' on macOS Terminal ✅
- python -m mytool --reverse hello > out.txt; xxd out.txt → ec 96 b4 ... 0a ✅
- python -m mytool --reverse 'Hello 世界' → '界世 olleH' ✅

## Findings
- LOW addressed inline (added zh + ja cases)
- MEDIUM deferred to issue #42

## Verdict
PASS — bug fixed with regression test.
```

### 8. Commit

The pre-commit hook runs all `pass` commands. They pass. Commit lands. The branch protection on `main` (separate concern) keeps it on a feature branch until reviewed.

## What this example shows

- A bug-fix without a regression test is a fix you cannot prove. The harness makes the test the gate.
- The triage phase (step 2) caught a "not actually a bug" hypothesis. The deep-interview skill exists for this.
- The 12-category ledger forced thinking about `compatibility` and `edge` even though the bug looked simple.
