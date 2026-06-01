"""AuditLog — gateway-facing wrapper around the hash-chained audit table.

design §7.2 + §5.3 + v0.5.3 R6. The chain implementation lives in
``mir.core.engine.memory.store.audit_append`` (already tested by
``tests/test_audit_chain.py``); this wrapper only gives the gateway a
``record(principal, tool, outcome, reason, **extra)`` shape matching the
design sketch.

Rationale for keeping the wrapper separate:
- The gateway shouldn't know about ``memory.store`` internals.
- Tests that exercise the gateway in isolation can inject a stub ``AuditLog``.
- Phase 2 (`security/signer_proxy.py`, F11) will replace the write path without
  touching the gateway — same public ``record`` signature.
"""
from __future__ import annotations

import sqlite3
from typing import Any

from mir.core.engine.memory import store


class AuditLog:
    """Thin facade. Thread-safe only insofar as the underlying sqlite3
    connection is used from a single coordinator (design §9.10 Engine write
    lock)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def record(
        self,
        principal: str,
        tool: str,
        outcome: str,
        reason: str = "",
        **extra: Any,
    ) -> str:
        payload: dict[str, Any] = {
            "principal": principal,
            "tool": tool,
            "outcome": outcome,
            "reason": reason,
        }
        if extra:
            payload["extra"] = extra
        return store.audit_append(self._conn, "tool_call", payload)

    def event(self, event: str, payload: dict[str, Any]) -> str:
        """Generic event path (hook_integrity_violation, hook3_violation, …).
        The gateway uses ``record``; internal subsystems use ``event``."""
        return store.audit_append(self._conn, event, payload)
