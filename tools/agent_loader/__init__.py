"""ADR-09 Phase 9A -- agent frontmatter loader.

Public API:
- AgentSpec -- dataclass returned by load_agent.
- AgentValidationError -- raised on schema violation.
- parse_frontmatter(path) -> dict -- read YAML-like frontmatter block.
- validate_frontmatter(data, mode) -> list[str] -- jsonschema check; mode in {'lenient', 'strict'}.
- load_agent(path, mode='lenient') -> AgentSpec -- parse + validate, raises AgentValidationError.

CLI:
- python -m tools.agent_loader <path> [--mode=lenient|strict]
  exit 0 = valid, 1 = validation error, 2 = file/parse error.

Schema: docs/templates/_schema/agent_frontmatter.schema.json (ADR-09 C2).
"""

from __future__ import annotations

from .loader import (
    AgentSpec,
    AgentValidationError,
    load_agent,
    parse_frontmatter,
    validate_frontmatter,
)

__all__ = [
    "AgentSpec",
    "AgentValidationError",
    "load_agent",
    "parse_frontmatter",
    "validate_frontmatter",
]
