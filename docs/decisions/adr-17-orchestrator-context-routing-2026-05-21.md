---
title: ADR-17 — Orchestrator-side context routing for specialist agents
status: accepted
date: 2026-05-21
accepted: 2026-05-21
acceptance_basis: P17-A schema + 7 specialist defaults landed (commit 9bbfe62) + P17-B main-orchestrator prompt integration (c18d80c) + P17-C dep-only asymmetry measurement (docs/operations/adr-17-routing-measure-2026-05-21.md). Asymmetry test PASS, finding parity PASS, token ratio 1.37× baseline reported (observation-driven, no pre-declared threshold per §S4).
revision: v2 (v1 + cold-review absorption: schema atomicity + Path.match flat-file + L3 override schema + measurement realism)
authors: [your-harness Harness orchestrator]
related:
  - adr-15-multi-agent-skill-catalog-2026-05-20.md
  - adr-16-specialist-deployment-2026-05-21.md
  - claude-codex-role-policy-2026-05-02.md
---

## 1. Context

ADR-15 P15-E (mini-spike v1 + v2, `docs/operations/adr-15-mini-spike-
2026-05-21.md`) empirically falsified the token-savings hypothesis at
the dispatch layer ADR-15 ships today. Treatment-lane combined token
usage was 2.66× baseline at 60 LOC and 2.69× baseline at 373 LOC. The
ratio is **structural** (each specialist reads the full changed-file
set; per-dispatch fixed cost is paid per specialist). It is not a
function of sample size.

The user has approved `cwe-auditor` and `dep-auditor` adoption despite
the miss (Q-E1, 2026-05-21 Discord). The remaining question — raised
as Q-E4 in the mini-spike report and as Q6 in the next-phase plan v4 §5
— is whether a follow-up ADR can change the routing so the hypothesis
holds. ADR-17 records the design for that follow-up.

The minimal change is **orchestrator-side input filtering** by a
catalog-declared scope pattern. Each specialist declares the file
patterns it reads. The orchestrator, when dispatching the specialist,
forwards only the files matching the pattern set. Files outside the
set never enter the specialist's fork context, so each specialist's
token cost grows with its own scope rather than with the full diff.

## 2. Decision

### S1 — Catalog field addition (additive optional)

Extend the schema `config/repo-agent-management.schema.json` agent
entry shape with an optional field:

```json
"scope_patterns": {
  "type": "array",
  "items": { "type": "string" },
  "default": ["**/*"],
  "description": "fnmatch glob patterns (relative to family root) that this specialist's fork context is filtered to. Default ['**/*'] preserves current no-filter behaviour. Implementation MUST use `fnmatch.fnmatch(path, pattern)` (or equivalent that handles flat root-level paths correctly), NOT `pathlib.Path.match`."
}
```

**Schema-JSON atomicity (v2 C1 resolution)**: P17-A acceptance hard
rule — the schema update (adding `scope_patterns` to
`$defs/catalog_agent.properties`) MUST land in the same atomic commit
as the catalog JSON entries gaining the field. The schema currently
has `additionalProperties: false` on `catalog_agent` (verified at
`config/repo-agent-management.schema.json` line 172). A two-step land
(schema first, JSON second, or vice versa) breaks every existing
manifest test mid-sequence.

**No `version` bump** (per ADR-15 §S2 migration pattern — additive
optional fields stay at root `version: 2`). The schema's
`additionalProperties: false` requires the new field be declared in
`properties`, but optionality (NOT in `required`) means existing
entries do not need to set it.

**Glob API choice (v2 C2 resolution)**: The implementation uses
`fnmatch.fnmatch(filepath_str, pattern)` from the Python stdlib
**not** `pathlib.Path.match`. Empirical fact: `Path('app.py').match
('**/*.py')` returns `False` on Python 3.9 + 3.12 — flat root-level
files are silently excluded by `Path.match`. `fnmatch.fnmatch
('app.py', '**/*.py')` returns `True`. The patterns in §S3 below
remain unchanged; the API choice is what makes them work for flat
paths. v1 §S1 said "Path.glob semantics" and v1 §R3 said "Path.match
style" — both are reverted to "fnmatch.fnmatch" with this v2 edit.

`repo-agent-management.json` `catalog.agents[<slug>]` entries gain the
field. For `proposed` and `external` agents we set the default
`["**/*"]`. For the two `active` specialists (cwe-auditor + dep-
auditor) we set domain-specific patterns per §S3.

### S2 — Orchestrator dispatch protocol

The your-harness orchestrator (Claude main session, the `main-orchestrator`
agent and its successors) consumes `scope_patterns` when preparing a
specialist's fork context:

1. Resolve the changed-file set for the task (typically `git diff
   --name-only HEAD~1` or the user-supplied scope).
2. For each specialist to dispatch:
   - Read `catalog.agents[<slug>].scope_patterns` from
     `repo-agent-management.json`.
   - Filter the changed-file set: keep file paths matching any pattern.
   - If the filtered set is **empty**, skip the dispatch entirely and
     log "specialist <slug> skipped — no files in scope".
   - Otherwise, pass the filtered list as the specialist's fork
     context.
3. Universal-tier agents (`main-orchestrator`, `executor-agent`,
   `codex-final-reviewer`, `quality-agent`) are NOT filtered — they
   always see the full file set. `scope_patterns` is meaningful only
   for `role: specialist` and `role: governance` entries.

This is an orchestration concern; it does not change `refresh-
specialists` (ADR-16), agent .md files (ADR-15), or
`repo-agent-management.schema.json` enforcement semantics. The
filtering happens at dispatch time, not at static analysis time.

### S3 — Default scope patterns

| Specialist | scope_patterns | Rationale |
|---|---|---|
| `cwe-auditor` | `["**/*.py", "**/*.js", "**/*.ts", "**/*.tsx", "**/*.go", "**/*.rs", "**/*.java", "**/*.kt", "**/*.c", "**/*.cc", "**/*.cpp", "**/*.h", "docs/security-policy.md", ".ai-harness/security-rules.md"]` | Source-code files in common languages + the security policy doc. Excludes docs, configs, lockfiles, test fixtures (caught by other lanes). |
| `dep-auditor` | `["requirements*.txt", "Pipfile*", "poetry.lock", "pyproject.toml", "package.json", "package-lock.json", "yarn.lock", "Cargo.toml", "Cargo.lock", "go.mod", "go.sum", "Gemfile", "Gemfile.lock", "build.gradle*", "pom.xml", "**/*.requirements"]` | Dependency manifests + lockfiles only. |
| `ui-reviewer` | `["**/*.tsx", "**/*.jsx", "**/*.vue", "**/*.svelte", "**/*.html", "**/*.css", "**/*.scss", "**/*-styles.dart", "**/*Screen.dart", "**/*Page.dart", "**/*Widget.dart"]` | UI component files in common frameworks. |
| `pipeline-validator` | `["**/dag/**", "**/pipelines/**", "**/etl/**", "**/airflow*/**", "**/*.airflow.yaml", "**/*.dvc", "**/schemas/**/*.json", "**/schemas/**/*.yaml"]` | Data pipeline definition + schema files. |
| `ontology-validator` | `["content/**/*.md", "ontology/**", "**/*.ontology.yaml", "**/*.taxonomy.yaml", "docs/content-model.md"]` | Content / ontology source files. |
| `runtime-contract-reviewer` | `["**/runtime/**", "**/exceptions.py", "**/errors.py", "**/*.error.ts", "tools/**/runtime_contract*"]` | Runtime exception + contract files. |
| `template-sync-validator` | `["**/CLAUDE.md", "**/AGENTS.md", "**/.claude/**", "**/.codex/**", "scripts/generate_codex_derivatives.sh", "config/repo-agent-management.json"]` | Sanitize-relevant template surfaces. |

These defaults are starting points. **L3 family overrides** (v2 C3
resolution) require an explicit schema surface — `agent_overrides` in
`repositories[i]` currently has only `add_specialists` /
`remove_specialists` (no scope-pattern override). P17-A schema update
MUST also extend `agent_overrides` shape with:

```json
"scope_patterns_overrides": {
  "type": "object",
  "description": "Per-specialist scope_patterns override at L3. Keys = specialist slug, values = replacement scope_patterns array (full override, not merge).",
  "additionalProperties": {
    "type": "array",
    "items": { "type": "string" }
  }
}
```

When a family's `agent_overrides.scope_patterns_overrides[<slug>]`
exists, the orchestrator uses it INSTEAD of the L1 catalog default.
Full replacement (not merge) — Q3 v1 decision retained.

If P17-A does not land this override surface, the L3 autonomy claim
in §S5 below is unbacked. v1 had this gap (advisory text without
schema surface).

### S4 — Measurement protocol (observation-driven, not threshold-gated)

**v2 H1 acknowledgement**: P17-C against the existing large fixture
is a **recalculation, not a new live run**. All 3 fixture files
(`payments.py` / `auth.py` / `integrations.py`) match cwe scope, so
cwe-auditor's input is identical to the unfiltered mini-spike v2
case. The only delta is that dep-auditor's filtered set is empty →
skipped dispatch → saved tokens. The "new" treatment total is simply
the existing cwe-only tally (29,602 from spike v2 §2.3 large
sample). Live signal requires the second fixture (see step 5 below).

After P17-A + P17-B land:

1. Re-compute (not re-run) the P15-E Task B large fixture
   (`docs/operations/adr15_mini_spike_large_fixture/`) with routing
   active. The fixture has 3 files: all 3 match cwe scope; dep-auditor
   scope is empty → skipped.
2. Report observed metrics:
   - baseline tokens (codex-final-reviewer full pass) — unchanged
     from mini-spike v2: 21,987.
   - treatment tokens (cwe-auditor full pass on filtered set +
     dep-auditor skipped). Predicted reduction = full
     dep-auditor cost saved, roughly 29,497 tokens dropped. New
     treatment combined token estimate: ~29,602 (cwe only).
   - new ratio: 29,602 / 21,987 = ~1.35×. Still over baseline, but
     **roughly half** of the v2 treatment cost.
3. Observe the actual measured ratio. **The ADR does NOT assert a
   pass/fail threshold.** It reports the observation. The user
   reviews the data and decides whether to extend routing to additional
   filtering axes (e.g., per-hunk slicing rather than per-file) or
   accept the current 1.35× ratio as the new operating cost.
4. The mini-spike fixture cannot demonstrate dep-auditor's benefit
   directly because it has no `requirements*.txt`. A second
   re-measure on a sample containing both code + dep manifest files
   is recommended in P17-C.
5. **(v2 M2 mitigation)** P17-C MUST include at least one
   **dep-only** sample (e.g., a fixture with `requirements.txt`
   change + no code files) to confirm dep-auditor fires when its
   scope is the only thing changed. This validates that the
   skip-on-empty-filter logic is correctly inverse: dep-only diff
   triggers dep-auditor, code-only diff skips it. Without this
   asymmetry test, the §S2 skip-dispatch policy creates a silent
   audit gap for diffs that touch only one specialist's scope.

### S5 — Backward compatibility

Catalog entries without `scope_patterns` default to `["**/*"]` (no
filtering, current behaviour). Migration is opt-in per specialist; no
forced backfill. ADR-15 §S2 enum [1, 2] versioning policy is
preserved.

### S6 — Out-of-scope (Will-NOT-do)

| # | Item | Reason |
|---|---|---|
| WN-1 | Per-hunk slicing inside files | Higher-order routing; revisit after S4 measurement |
| WN-2 | Semantic chunking via AST | Same |
| WN-3 | Per-import filtering (cwe-auditor sees only files importing security-sensitive modules) | Same; current pattern-based approach is the minimum viable change |
| WN-4 | Enforcement (orchestrator rejects dispatches that ignore scope_patterns) | Advisory only; main-orchestrator self-applies, but no hook check |
| WN-5 | Catalog `scope_patterns` syntax beyond glob | Keep simple; if richer DSL needed, future ADR |
| WN-6 | Filtering universal-tier agents | They always see full scope by design |

## 3. Consequences

- Specialist token cost scales with specialist scope, not full diff.
- The "no work" case (specialist scope empty for this task) becomes a
  skipped dispatch with explicit log — saves the full per-dispatch
  fixed cost.
- The token-savings hypothesis becomes testable. Whether it holds
  depends on the diff's file mix.
- Adding new specialists in future ADRs requires their
  `scope_patterns` to be set explicitly (or default to `["**/*"]`
  with a note that routing is disabled for that agent).
- `main-orchestrator` and successors gain a new responsibility:
  reading the catalog at dispatch time. This is a small, additive
  prompt instruction; no code changes outside the orchestrator's own
  body until P17-B.

## 4. Implementation Phases (P17-X)

| Phase | Action |
|---|---|
| **P17-A** | Schema atomic update — adds `scope_patterns` to `$defs/catalog_agent.properties` + `scope_patterns_overrides` to `agent_overrides` in `repositories[i]` — in the SAME commit as catalog JSON gaining defaults for 7 specialists + verifier WARN on missing `scope_patterns` for `status: active` specialists (advisory). No orchestrator change. **(v2 C1)** schema-JSON atomicity mandatory. |
| **P17-B** | Orchestrator integration: update `main-orchestrator` agent body to consume `scope_patterns` at dispatch. **(v2 H2)** catalog read mechanism: main-orchestrator body instructs the orchestrator to issue an explicit `Read` tool call on `config/repo-agent-management.json` once at session start, or per-dispatch if session-level cache is stale. The catalog is small (<10KB JSON in current state) so per-session read is cheap. New ledger entry (or extension of an existing one) records which scope_patterns were used per dispatch — feeds re-measurement. |
| **P17-C** | Re-compute large-fixture ratio (v2 H1 — recalculation, not new run) + run dep-only fixture (v2 M2 — new live measurement). Report observed ratios + decide next routing layer (or stop). |

P17-A can land independently of P17-B (read-only metadata). P17-B
requires user review of P17-A's first deployment evidence before
proceeding (per plan-next-phase v4 §5 Issue 6 resolution).

## 5. Risks

- **R1**: Glob patterns may miss future file extensions / framework
  conventions. Mitigation: keep patterns conservative-ish; per-family
  L3 override; add patterns via PR as the fleet evolves.
- **R2**: Empty-filtered-set skip may hide real findings if patterns
  exclude relevant files. Mitigation: log every skip explicitly;
  re-measure (S4 step 4) catches the case where a known seeded defect
  in a non-matching file is missed.
- **R3**: Pattern-matching adds orchestrator-side complexity. your-harness
  main-orchestrator becomes a non-trivial filter. Mitigation: use
  `fnmatch.fnmatch(filepath_str, pattern)` from the Python stdlib
  (v2 C2 — Path.match has a documented flat-file gap with `**`
  prefix; fnmatch handles flat paths correctly); no compiled regex;
  no external glob libraries.
- **R4**: Public template sync may carry scope_patterns that aren't
  applicable to public consumers' diffs. Mitigation: sanitize step
  for public template strips family-specific patterns and reverts to
  `["**/*"]` default.
- **R5**: P17-B orchestrator change risks a regression in already-
  measured token costs. Mitigation: P17-C compares against the
  mini-spike v2 baseline; any uplift (treatment costs more than
  before routing) is a stop signal.

## 6. Open Questions

- **Q1**: Should `scope_patterns` allow exclusion patterns (e.g.,
  `["!**/test_*.py"]`)? P17-A could ship include-only and add
  exclusion in P17-B if S4 measurement shows test files dominate the
  cwe-auditor scope.
- **Q2**: Universal-4 agents (orchestrator/executor/reviewers) — does
  the orchestrator-side filtering apply to `codex-final-reviewer` and
  `quality-agent` even if their `role: review`? Current §S2 says no.
  Revisit if S4 measurement shows reviewers dominate the cost.
- **Q3**: Per-family L3 override syntax for `scope_patterns` — JSON
  patch (`add` / `remove`) or full override? Recommend full override
  with explicit catalog comment ("derived from default at <commit>").
- **Q4**: When a specialist is dispatched with an empty filtered set
  and skipped, does the universal-4 review chain still need to cover
  that specialist's scope? Yes — universal reviewers always run. The
  specialist skip is an optimization, not a substitute.
- **Q5**: ADR-17 P17-B orchestrator integration interacts with the
  existing `main-orchestrator` prompt — at what level does the
  prompt instruct the orchestrator to read catalog vs hardcode the
  matching logic? Recommend prompt-level instruction with a single
  catalog-reading helper; no Python code change in P17-B if the
  orchestrator can do the matching as part of its dispatch prompt.

## 7. BORROWED-FROM

```
BORROWED-FROM: self/docs/decisions/adr-15-multi-agent-skill-catalog-2026-05-20.md
  - §S1 L1 catalog as single source of truth (extended here with
    scope_patterns field)
  - §S2 additive-optional-field migration pattern (no version bump)
  - §S3 specialist scope text (informs default scope_patterns in §S3)

BORROWED-FROM: self/docs/decisions/adr-16-specialist-deployment-2026-05-21.md
  - §S2 ledger pattern (not used directly; surface acknowledgement)
  - §S6 WN-5 (back-sync limitation — applies equally to scope_patterns)

BORROWED-FROM: self/docs/operations/adr-15-mini-spike-2026-05-21.md
  - §2.4 token ratio root-cause analysis (each specialist reads full
    changed-file set) — the empirical observation that motivates this
    ADR

BORROWED-FROM: self/memory/project_mir_governance_principles.md
  - Principle 1: per-family autonomy (L3 override authority over
    scope_patterns)
```

**External prior-art cross-check (v2 M1)**: reviewed GitHub Actions
`on.push.paths` filter and pre-commit's per-hook `files` /
`types` pattern. Both apply glob filters to changed-file lists as a
trigger gate. ADR-17 is semantically equivalent but scope is
catalog-metadata + orchestrator-side dispatch (not CI-trigger-side).
**No code borrowed** from either. The design is a direct, project-
specific application of the same pattern shape rather than a port.
`feedback_borrow_first.md` declaration: pattern recognized,
implementation independent.

## 8. Acceptance

- [x] **P17-A** (atomic schema+JSON commit per v2 C1):
  `repo-agent-management.schema.json` `$defs/catalog_agent.properties`
  gains `scope_patterns` (optional, array of string). `$defs/agent_overrides`
  gains `scope_patterns_overrides` (optional, object of slug→array).
  Catalog JSON adds default `scope_patterns` for the 7 specialists per
  §S3. Verifier emits WARN on missing field for `role: specialist,
  status: active` entries (advisory).
- [x] **P17-A**: regression — `uv run pytest -q` ≥ 2410 passed
  (HEAD baseline at commit 156d1ce; v2 H3 pin) + new tests.
- [x] **P17-A**: catalog change does NOT bump root `version` field
  (must remain `version: 2`).
- [x] **P17-B**: `main-orchestrator` agent body instructs the
  orchestrator to (a) read `config/repo-agent-management.json` once
  at session start via `Read` tool, (b) filter each specialist's
  fork context by its `scope_patterns` at dispatch, (c) honor any
  per-family `scope_patterns_overrides` for non-meta families.
- [x] **P17-B**: dispatch log entry (per ADR-18 P18-C if landed, or
  a standalone log) captures the scope_patterns applied + filtered-
  file count + skipped slugs.
- [x] **P17-C** (v2 H1 + M2): two measurements.
  (a) Re-compute the existing large-fixture ratio with dep-auditor
      skipped — this is a calculation, not a live run.
  (b) Live run on a **dep-only fixture** (requirements.txt change +
      no code) to confirm dep-auditor fires when code-only diffs
      would have skipped it. Saves the asymmetry test from being
      omitted by accident.
  Report both in `docs/operations/adr-17-routing-measure-<date>.md`.
  No pre-declared pass/fail threshold. User reviews and decides
  P17-B accept or next routing layer (per-hunk, AST).
- [x] codex-final-reviewer cold review on ADR-17 v2: READY.
- [x] ADR-17 status → accepted after P17-A + P17-B + P17-C complete
  with user approval.

## 9. Revision history

- v1 (2026-05-21): initial draft. Motivated by P15-E v2 mini-spike
  token-ratio observation. Recommendation = catalog-declared
  scope_patterns + orchestrator-side filtering (additive optional
  field, no schema version bump per ADR-15 §S2 pattern). Observation-
  driven S4 measurement with no fabricated threshold.
- **v2 (2026-05-21)**: codex-final-reviewer cold-review absorption
  (3 CRITICAL + 3 HIGH + 3 MAJOR):
  - C1 (schema atomicity): P17-A schema-JSON same-commit mandate;
    `additionalProperties: false` requires explicit field declaration.
  - C2 (Path.match flat-file): glob API revised to `fnmatch.fnmatch`;
    §S1 + §R3 reconciled.
  - C3 (L3 override schema): `agent_overrides.scope_patterns_overrides`
    sub-field added to P17-A scope.
  - H1 (measurement recalculation honesty): §S4 step 1 reframed as
    re-compute, not re-run.
  - H2 (orchestrator catalog access): P17-B specifies `Read` tool
    call at session start.
  - H3 (baseline drift): §8 P17-A pins ≥ 2410 (current HEAD
    156d1ce).
  - M1 (prior-art declaration): §7 explicitly declares the GitHub
    Actions / pre-commit pattern recognition.
  - M2 (single-type-diff audit gap): §S4 step 5 mandates dep-only
    fixture for asymmetry validation.
  - M3 (dep-auditor flat-file): same fnmatch API fix as C2 covers
    `**/*.requirements`.
