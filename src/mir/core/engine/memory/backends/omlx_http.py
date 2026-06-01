"""oMLX HTTP embedding backend.

BORROWED-FROM: claude_memory@d0e523cd06d6adeae4744d89736f79564d9db41d
  lib/claude_memory/index/vector_index.rb#VectorIndex
License: MIT
Changes:
  - Ruby → Python, HTTP client via httpx.
  - L2-norm + shape assertion per v0.5.3 R3 (norm_tolerance default 1e-3).
  - Endpoint is OpenAI-compatible (oMLX proxy exposes it); model id is the
    proxy-facing value `bge-m3-mlx-fp16` (HF: mlx-community/bge-m3-mlx-fp16).

design §5.2 · §9.7 · integrations/omlx-adapter.md.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

from mir.core.config.defaults import (
    DEFAULT_EMBEDDING_API_KEY_ENV,
    DEFAULT_EMBEDDING_BASE_URL,
    DEFAULT_EMBEDDING_DIM,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_NORM_TOLERANCE,
    DEFAULT_EMBEDDING_TIMEOUT_SEC,
)


class EmbeddingShapeError(RuntimeError):
    """encode() returned vectors with the wrong dimension."""


class EmbeddingNotNormalizedError(RuntimeError):
    """encode() returned a vector whose L2 norm is outside tolerance."""


@dataclass(frozen=True)
class _BackendCfg:
    base_url: str
    model: str
    dim: int
    timeout_sec: int
    norm_tolerance: float
    api_key_env: str
    auth_scheme: str


class OmlxHttpBackend:
    """Sync HTTP backend; thread-safe enough for per-call use.

    Callers must inject `_BackendCfg` (built from ResolvedConfig); no
    fallback to env lookups for anything other than the API key itself.
    That keeps the class test-friendly — the whole object is derivable
    from the frozen config.
    """

    def __init__(self, cfg: _BackendCfg):
        self._cfg = cfg
        key = os.environ.get(cfg.api_key_env, "")
        headers: dict[str, str] = {}
        if key:
            headers["Authorization"] = f"{cfg.auth_scheme} {key}"
        self._client = httpx.Client(
            base_url=cfg.base_url,
            timeout=cfg.timeout_sec,
            headers=headers,
        )

    @property
    def dimensions(self) -> int:
        return self._cfg.dim

    def encode(self, texts: list[str]) -> list[list[float]]:
        r = self._client.post(
            "/embeddings",
            json={"model": self._cfg.model, "input": texts},
        )
        r.raise_for_status()
        vectors: list[list[float]] = [row["embedding"] for row in r.json()["data"]]
        for i, v in enumerate(vectors):
            if len(v) != self._cfg.dim:
                raise EmbeddingShapeError(
                    f"row {i}: dim={len(v)} != {self._cfg.dim}"
                )
            norm = sum(x * x for x in v) ** 0.5
            if abs(norm - 1.0) > self._cfg.norm_tolerance:
                raise EmbeddingNotNormalizedError(
                    f"row {i}: L2 norm={norm:.6f} "
                    f"(tol={self._cfg.norm_tolerance})"
                )
        return vectors

    def close(self) -> None:
        self._client.close()


def build_default() -> OmlxHttpBackend:
    """Wire the backend from defaults.py — intentional single source."""
    return OmlxHttpBackend(_BackendCfg(
        base_url=DEFAULT_EMBEDDING_BASE_URL,
        model=DEFAULT_EMBEDDING_MODEL,
        dim=DEFAULT_EMBEDDING_DIM,
        timeout_sec=DEFAULT_EMBEDDING_TIMEOUT_SEC,
        norm_tolerance=DEFAULT_EMBEDDING_NORM_TOLERANCE,
        api_key_env=DEFAULT_EMBEDDING_API_KEY_ENV,
        auth_scheme="Bearer",
    ))


def from_config(cfg: Any) -> OmlxHttpBackend:
    """Build from a ``_EmbeddingCfg`` (pydantic, see ``core/config/loader.py``).

    Typed as ``Any`` to keep this module free of a hard import on the config
    loader (which imports defaults from this tree). Structural contract: the
    argument must expose ``base_url`` / ``model`` / ``dim`` / ``timeout_sec`` /
    ``norm_tolerance`` / ``api_key_env`` / ``auth_scheme``.
    """
    return OmlxHttpBackend(_BackendCfg(
        base_url=cfg.base_url,
        model=cfg.model,
        dim=cfg.dim,
        timeout_sec=cfg.timeout_sec,
        norm_tolerance=cfg.norm_tolerance,
        api_key_env=cfg.api_key_env,
        auth_scheme=cfg.auth_scheme,
    ))
