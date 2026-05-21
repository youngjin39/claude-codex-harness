---
name: knowledge
description: "Knowledge ingest and lint for the shared wiki/knowledge graph.\n\nTrigger: knowledge, wiki, ingest, knowledge graph, knowledge lint\n\nAbsorbs: knowledge-ingest, knowledge-lint"
---

# Knowledge

## Use When
- When ingesting an external source into the shared wiki or knowledge graph.
- When health-checking the LLM Wiki for contradictions, stale claims, orphans, or gaps.

## Absorbed legacy skills
- knowledge-ingest — Ingest external source into LLM Wiki. Raw to wiki pages + log.
- knowledge-lint — Health-check the LLM Wiki. Contradictions, stale claims, orphans, gaps.

## Workflow
1. Identify which absorbed legacy intent applies (design vs. plan vs. interview etc.).
2. Refer to the archived legacy SKILL.md under `archive/skills/<legacy>/` for original workflow.
3. Output per absorbed legacy's protocol.

## Status
This skill is the canonical entry point. Legacy slugs remain dispatchable until P15-I archive completes.
