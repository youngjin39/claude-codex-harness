"""Canonical JSON serialisation — shared helper for signing payloads.

Third Review TH2: promoted from mir.core.migrate.manifest.canonical_json
so BackupManifest, PhaseCompletionToken (ADR 3 §2.2.1), and
preserve_writer tokens (ADR 2 §2.3.2) all use the same byte-stable
serialisation before Ed25519 signing.

Sorted keys + compact separators + UTF-8 (no ASCII escape) is what makes
the output stable across Python versions and platforms.
"""
from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel


def canonical_json(
    payload: BaseModel | dict[str, Any],
    *,
    omit: tuple[str, ...] = ("signature",),
) -> str:
    """Serialise *payload* to its canonical signing-ready JSON form.

    ``payload`` may be a pydantic BaseModel (any frozen/unfrozen model) or
    a plain dict. ``omit`` names are removed from the top-level mapping
    before serialisation — the default matches BackupManifest's signature
    carve-out so callers do not need to spell it out.
    """
    if isinstance(payload, BaseModel):
        body = payload.model_dump()
    else:
        body = dict(payload)
    for key in omit:
        body.pop(key, None)
    return json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
