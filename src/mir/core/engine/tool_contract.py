"""Mir tool contract obligatory fields (phase-4 §4).

Every tool call should declare a ToolContract with the 4 obligatory fields.
The contract is recorded in tool_event.json and validated at hook entry.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolContract:
    """4 obligatory phase-4 §4 fields.

    Fields:
        idempotency_key: unique-per-side-effect string
        precondition: declared state requirement (free-form for now;
            future: structured enum)
        dry_run: bool; true = simulate only
        side_effect_summary: 1-line human description (max 200 char)
        extra: optional dict for tool-specific metadata
    """
    idempotency_key: str
    precondition: str
    dry_run: bool
    side_effect_summary: str
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if not d["extra"]:
            d.pop("extra")
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ToolContract:
        for required in ("idempotency_key", "precondition", "dry_run",
                         "side_effect_summary"):
            if required not in d:
                raise ValueError(f"missing required field: {required}")
        if len(d["side_effect_summary"]) > 200:
            raise ValueError(
                f"side_effect_summary too long: {len(d['side_effect_summary'])} chars (max 200)"
            )
        return cls(
            idempotency_key=d["idempotency_key"],
            precondition=d["precondition"],
            dry_run=d["dry_run"],
            side_effect_summary=d["side_effect_summary"],
            extra=d.get("extra", {}),
        )

    @classmethod
    def from_json(cls, s: str) -> ToolContract:
        return cls.from_dict(json.loads(s))


def make_idempotency_key(*parts: str) -> str:
    """Deterministic key from string parts. Same parts → same key.

    Use for tool calls where re-execution should be safe (e.g.,
    make_idempotency_key('write_file', path, content_hash)).
    """
    joined = "|".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


class ContractViolation(Exception):
    """Raised when a tool call lacks required contract or violates a field."""
