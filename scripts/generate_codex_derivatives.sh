#!/bin/bash
# Codex TOML derivative generator stub.
#
# Referenced from the header line of every .codex/agents/*.toml file
# ("GENERATED FILE: ... rerun scripts/generate_codex_derivatives.sh"),
# from docs/decisions/adr-09-execution-backend-frontmatter.md, and from
# config/repo-agent-management.json tracked_paths entries.
#
# This template ships a stub. A real implementation would:
#   - Read .claude/agents/<slug>.md sources (frontmatter + body).
#   - Strip the YAML frontmatter and convert the body into a Codex TOML
#     `developer_instructions` block.
#   - Write .codex/agents/<slug>.toml with a generated-file header.
#   - Skip Claude-only agents that have no Codex execution lane.
#
# Mirror generation is optional for first-boot harness usage — the
# .claude/agents/*.md files are the source of truth and Codex can read
# them directly via tools.agent_loader. The .toml mirrors exist as an
# optimization for Codex CLI session bootstrap.
#
# Customize for your project — or remove the TOML mirrors and update
# the references if your fleet does not use the .codex/agents/ pattern.

cat <<'USAGE'
generate_codex_derivatives.sh — stub

This template ships a placeholder. The full Codex TOML derivative
generator is not bundled — implement it for your fleet OR maintain
the .codex/agents/*.toml files by hand. The Claude-side .md sources
under .claude/agents/ are the source of truth.

To regenerate a single TOML by hand from its .md source:
  1. Copy the .md body into a TOML developer_instructions block.
  2. Preserve the ADR-18 §S2 callout header for agents declaring
     execution_backend: codex.
  3. Update the generated-file header line.

The 12 agents that ship in this template are already in sync. You
only need to regenerate if you edit the .md sources.

USAGE
exit 0
