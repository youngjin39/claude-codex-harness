"""Memory layer — sqlite + FTS5 + sqlite-vec + sanitize + distill.

Public re-exports only. Internal modules are imported lazily by CLI / gateway
so that `from mir.core.engine.memory import …` never triggers sqlite3 at
import time in tests that only need the contracts leaf.
"""
from __future__ import annotations

from .predicates import PREDICATE_MAP, canonicalize
from .sanitize import sanitize

__all__ = ["sanitize", "canonicalize", "PREDICATE_MAP"]
