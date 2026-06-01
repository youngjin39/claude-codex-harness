"""Instance ID resolution — same workstation identifier (design §9.17 R5).

Used by both Meta mode approvals and ``mir nuke`` tokens: a signed
payload that includes ``instance_id`` cannot be replayed on a
different workstation even if the attacker copied the ``memory.db`` and
the user's private key.

Resolution order (first hit wins):

  1. ``/etc/machine-id``           — systemd-distro canonical ID
  2. ``/var/lib/dbus/machine-id``  — dbus fallback (older distros)
  3. ``/sys/class/dmi/id/product_uuid``  — x86 hardware UUID (root on most
     distros; skipped if unreadable)
  4. ``platform.node()`` + schema SHA of ``memory.db`` initial migration — portable fallback

The fallback is derived from two stable-per-host facts: the hostname
and the SHA of migration 001_claude_memory_schema.sql. Copying memory.db
to a different host changes ``platform.node()`` → different
``instance_id`` → every Meta/nuke token issued for the original host
fails verification.

``platform.node()`` alone would be weak (hostnames collide), so we mix
in the schema SHA to tie the identity to this specific Mir install.
"""
from __future__ import annotations

import hashlib
import platform
from functools import lru_cache
from pathlib import Path

_MACHINE_ID_FILES: tuple[Path, ...] = (
    Path("/etc/machine-id"),
    Path("/var/lib/dbus/machine-id"),
    Path("/sys/class/dmi/id/product_uuid"),
)


def _read_stripped(path: Path) -> str | None:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return value or None


def _fallback_id() -> str:
    """Hostname + schema SHA → deterministic per-install identifier."""
    # migrations live alongside the runtime; resolving relative to the
    # importing package keeps this honest if Mir is installed as a wheel.
    mig_root = Path(__file__).resolve().parent / "memory" / "migrations"
    initial = mig_root / "001_claude_memory_schema.sql"
    h = hashlib.sha256()
    h.update(platform.node().encode("utf-8") or b"unknown")
    try:
        h.update(initial.read_bytes())
    except OSError:
        # No migrations installed yet (pre-Step 2 state) — fall back to a
        # fixed marker so the hash is stable across boots.
        h.update(b"mir-initial-schema-missing")
    return h.hexdigest()


@lru_cache(maxsize=1)
def current_instance_id() -> str:
    """Lazy-computed, cached. Call via ``lru_cache`` to keep the cost at
    one file read per process. Tests that need to override call
    ``current_instance_id.cache_clear()``."""
    for path in _MACHINE_ID_FILES:
        value = _read_stripped(path)
        if value:
            return value
    return _fallback_id()


__all__ = ("current_instance_id",)
