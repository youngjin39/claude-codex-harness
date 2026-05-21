---
name: automation
description: "Long-running task control + browser automation.\n\nTrigger: runner, long-running, background, monitor, resume, compact, handoff, browser, scrape, E2E\n\nAbsorbs: runner, browser-automation"
---

# Automation

## Use When
- When a task is long-running or must survive session restart, compact, or handoff.
- When browser automation, scraping, E2E testing, or web-app operation is needed.

## Absorbed legacy skills
- runner — Long-running/background task control for Codex and Claude. Externalize task state to a durable ledger so compact, handoff, and session resume reconnect to the same work instead of relaunching it.
- browser-automation — Real-browser control via agent-browser CLI. Accessibility-tree snapshots for token-efficient page interaction.

## Workflow
1. Identify which absorbed legacy intent applies (design vs. plan vs. interview etc.).
2. Refer to the archived legacy SKILL.md under `archive/skills/<legacy>/` for original workflow.
3. Output per absorbed legacy's protocol.

## Status
This skill is the canonical entry point. Legacy slugs remain dispatchable until P15-I archive completes.
