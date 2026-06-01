"""EmbeddingBackendRegistry — `mir.embedding_backends` entry_points.

design §5.2 · §8.4 (V9). Phase 1 기본 구현 = OmlxHttpBackend (Step 2 실장).
"""
from __future__ import annotations

from .base import EntryPointRegistry


class EmbeddingBackendRegistry(EntryPointRegistry):
    GROUP = "mir.embedding_backends"
