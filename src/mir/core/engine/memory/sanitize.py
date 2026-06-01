"""Sanitize — redact `<private>` / `<secret>` / `<noindex>` blocks.

BORROWED-FROM: claude_memory@d0e523cd06d6adeae4744d89736f79564d9db41d
  lib/claude_memory/privacy_tag.rb#sanitize
BORROWED-FROM: claude_memory@d0e523cd06d6adeae4744d89736f79564d9db41d
  lib/claude_memory/content_sanitizer.rb#strip_blocks
License: MIT
Changes:
  - Ruby `/m` → Python `re.DOTALL` (v0.5.2 BLOCKER O3).
  - `consent_scope` kwarg preserves `<private>` when caller is operating
    inside a consented boundary (O10).

Contract (see tests/test_sanitize.py):
  1. Every block pattern compiles with `_FLAGS` (re.DOTALL | re.IGNORECASE).
  2. Multi-line blocks are fully redacted.
  3. `consent_scope="persistent"` keeps `<private>` intact but still strips
     `<secret>` and `<noindex>`.
"""
from __future__ import annotations

import re

# Flags shared by every block pattern. Adding a new pattern without this
# constant would silently re-introduce the O3 bug, so tests enforce it.
_FLAGS = re.DOTALL | re.IGNORECASE

_PRIVATE = re.compile(r"<private>(.+?)</private>", _FLAGS)
_SECRET = re.compile(r"<secret>(.+?)</secret>", _FLAGS)
_NOINDEX = re.compile(r"<noindex>(.+?)</noindex>", _FLAGS)

_ALWAYS_REDACT: tuple[re.Pattern[str], ...] = (_SECRET, _NOINDEX)


def sanitize(src: str, *, consent_scope: str = "ephemeral") -> str:
    """Redact private-content tags.

    `consent_scope`:
      - `"ephemeral"` (default): all three tags are redacted.
      - `"persistent"`: `<private>` is preserved (caller has consent);
        `<secret>` / `<noindex>` are still redacted.
    """
    out = _PRIVATE.sub("[REDACTED]", src) if consent_scope != "persistent" else src
    for pat in _ALWAYS_REDACT:
        out = pat.sub("[REDACTED]", out)
    return out
