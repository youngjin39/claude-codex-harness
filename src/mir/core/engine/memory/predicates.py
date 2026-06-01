"""Predicate canonicalization.

BORROWED-FROM: codenamev/claude_memory@d0e523cd06d6adeae4744d89736f79564d9db41d
  db/migrations/014_canonicalize_predicates.rb#PredicateMap
License: MIT
Changes:
  - Ruby PredicateMap adapted to a Python read-only mapping.
  - Lookup is case-insensitive and whitespace-trimmed.

Design §9.19: `distill.py` routes every new predicate through
`canonicalize(...)` before INSERT, and migration 014 normalizes anything
that slipped in before this map existed.
"""
from __future__ import annotations

from types import MappingProxyType

_SEED: dict[str, str] = {
    "use": "use",
    "uses": "use",
    "used": "use",
    "using": "use",
    "call": "call",
    "calls": "call",
    "called": "call",
    "calling": "call",
    "depend on": "depend_on",
    "depends on": "depend_on",
    "depended on": "depend_on",
    "depending on": "depend_on",
    "import": "import",
    "imports": "import",
    "imported": "import",
    "extend": "extend",
    "extends": "extend",
    "extended": "extend",
    "implement": "implement",
    "implements": "implement",
    "implemented": "implement",
    "reference": "reference",
    "references": "reference",
    "referenced": "reference",
}

# Read-only view — callers MUST NOT mutate this map.
PREDICATE_MAP: MappingProxyType[str, str] = MappingProxyType(_SEED)


def canonicalize(predicate: str) -> str:
    """Return the canonical predicate, or the normalized input if unknown."""
    key = predicate.lower().strip()
    return PREDICATE_MAP.get(key, key)
