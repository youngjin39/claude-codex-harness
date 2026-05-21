---
name: bluebricks
description: "Mandatory workflow for code writing, code analysis, debugging, refactoring, architecture review, PR review, repository exploration, dependency analysis, and bluebricks-based development.\n\nTrigger: code, debug, refactor, architecture, module, repository, PR review, bluebrick, dependency"
---

# AI-Ready Bluebricks Development

## Use When
- The task involves program development or codebase analysis.
- The task touches multiple files, boundaries, or hidden project rules.
- The task needs architecture, dependency, hazard, or validation awareness.

Do not use this skill for pure writing, research, summaries, or other non-code tasks.

## Required Reads
Before non-trivial code work, read:
- `.ai-harness/development-ai-rules.md`
- `.ai-harness/bluebricks.md`
- `.ai-harness/tdd-matrix.md`
- `.ai-harness/deny-list.yaml`
- `.ai-harness/failure-patterns.md` when repeated mistakes or hazards may matter

## Workflow
1. Define the exact task boundary.
2. Identify the affected module or bluebrick.
3. Answer WHAT / HOW / HOW NOT / WHERE / WHY for the relevant boundary.
4. Decide whether the work is local, cross-module, or orchestration-level.
5. Apply role policy: Claude plans and controls; Codex writes code, runs composite TDD, and performs code review by default.
6. If Codex is not the execution lane, record the override reason in `tasks/plan.md` or the active handoff before touching implementation code.
7. Create or update `tasks/tdd.json` before editing implementation code.
8. Classify every mandatory TDD category: `unit`, `integration`, `e2e`, `browser`, `edge`, `architecture`, `availability`, `load`, `soak`, `security`, `compatibility`, `transaction_locking`.
9. Use the smallest safe change.
10. Run the applicable validation commands declared in `tasks/tdd.json` first.
11. Record newly discovered hazards or failure patterns in `.ai-harness/`.

## Bluebrick Checklist
For each affected bluebrick, identify:
- purpose
- public interface
- internal rules
- non-obvious hazards
- dependencies
- downstream users
- composition relationship
- orchestration flow
- validation method

## Context Hygiene
- One session = one task.
- Avoid repeated file reads when the file has not changed.
- Do not dump huge logs or whole diffs into context.
- Use bounded output and targeted commands.

## Sub-agent Policy
Use sub-agent for:
- broad codebase search
- PR review
- security review
- performance investigation
- multi-file dependency analysis
- test failure investigation
- architecture comparison

Do not use sub-agent for:
- single grep
- reading one known file
- small local edits
- small diff review

## Safe Modification Rules
- Preserve architecture boundaries.
- Do not silently expand scope.
- Do not edit generated files unless generation is the task.
- Do not edit merged migration files; create a new one.
- Do not remove legacy fields without dependency checks.

## Validation Order
1. commands declared by applicable composite TDD categories in `tasks/tdd.json`
2. lint or typecheck
3. build
4. full test suite only when necessary

Codex review is the default adversarial pass. Executed composite TDD evidence is the primary proof. Claude-side review is fallback or synthesis unless a role override is explicitly approved.

## Final Response
When finishing, report:
1. summary
2. changed files
3. validation performed
4. risks or assumptions
5. newly discovered AI-ready rules, if any
