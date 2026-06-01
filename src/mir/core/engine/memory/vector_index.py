"""Vector index — EmbeddingBackend protocol + sqlite-vec helpers.

BORROWED-FROM: codenamev/claude_memory@d0e523cd06d6adeae4744d89736f79564d9db41d
  lib/claude_memory/index/vector_index.rb#VectorIndex
License: MIT
Changes:
  - Ruby vector index adapted to a Python backend protocol.
  - concrete oMLX HTTP backend lives in backends/omlx_http.py.
  - embedding shape and finite-value checks run before sqlite-vec packing.

design §5.2 (oMLX HTTP + 1024-dim) · §5.1/§5.3 (vec0 table) · §7.6
(hardening) · §9.9 (graceful degradation).

Backend implementations register via the `mir.embedding_backends` entry
point. No concrete backend is imported here — `OmlxHttpBackend` lives in
`backends/omlx_http.py` and is discovered through the registry.
"""
from __future__ import annotations

import math
import struct
from typing import Protocol, runtime_checkable

from mir.core.config.defaults import DEFAULT_EMBEDDING_DIM


@runtime_checkable
class EmbeddingBackend(Protocol):
    """Structural contract. CAO-style runtime_checkable Protocol (v0.5.3 A4)."""

    @property
    def dimensions(self) -> int: ...

    def encode(self, texts: list[str]) -> list[list[float]]: ...


# --- validation (F4 hardening) ---

# bge-m3 outputs are L2-normalised so every component is in [-1, 1]. A wider
# guard band tolerates adapter quantisation drift while still catching
# obviously-broken embeddings (e.g. "1e38" from a misconfigured backend).
_DEFENSIVE_BOUND = 10.0


def validate_embedding(
    vec: list[float], *, expected_dim: int = DEFAULT_EMBEDDING_DIM
) -> None:
    """Raise ``ValueError`` if ``vec`` is the wrong shape, contains NaN/Inf,
    or has any component outside the defensive bound.

    design §7.6 F4. Called from ``upsert_vector`` before packing so a bad
    embedding can never reach sqlite-vec's float32 storage (where NaN would
    quietly corrupt distance queries).
    """
    if len(vec) != expected_dim:
        raise ValueError(
            f"embedding length {len(vec)} != expected dim {expected_dim}"
        )
    for i, x in enumerate(vec):
        if not math.isfinite(x):
            raise ValueError(f"embedding[{i}] is not finite: {x!r}")
        if abs(x) > _DEFENSIVE_BOUND:
            raise ValueError(
                f"embedding[{i}]={x!r} exceeds defensive bound "
                f"±{_DEFENSIVE_BOUND}"
            )


# --- vec0 table helpers ---

def _pack_vector(v: list[float]) -> bytes:
    """sqlite-vec `float[N]` columns expect little-endian float32 bytes."""
    return struct.pack(f"{len(v)}f", *v)


def ensure_vec_table(
    conn, *, dim: int = DEFAULT_EMBEDDING_DIM, table: str = "facts_vec"
) -> None:
    """Create the vec0 virtual table if sqlite-vec is loaded.

    Caller should check `Connection.vec_available` before calling — this
    function will raise if the extension is absent.
    v0.5.3 V8: lowercase `float[NNN]` is mandatory; sqlite-vec rejects upper.
    """
    conn.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS {table} "
        f"USING vec0(embedding float[{dim}])"
    )


def upsert_vector(
    conn,
    rowid: int,
    vector: list[float],
    *,
    table: str = "facts_vec",
    expected_dim: int = DEFAULT_EMBEDDING_DIM,
) -> None:
    validate_embedding(vector, expected_dim=expected_dim)
    conn.execute(
        f"INSERT OR REPLACE INTO {table}(rowid, embedding) VALUES (?, ?)",
        (rowid, _pack_vector(vector)),
    )


def knn(
    conn, query: list[float], k: int, *, table: str = "facts_vec"
) -> list[tuple[int, float]]:
    """Return top-k (rowid, L2 distance) pairs nearest to `query`."""
    cur = conn.execute(
        f"SELECT rowid, distance FROM {table} "
        f"WHERE embedding MATCH ? ORDER BY distance LIMIT ?",
        (_pack_vector(query), k),
    )
    return list(cur.fetchall())
