"""Mir Registry 4종 — entry_points 기반 확장 지점.

design §8.4 · V9 · H9.
하드코딩 금지 원칙: 이 패키지 내부에서 클래스 literal dict 금지.
추가는 `pyproject.toml [project.entry-points."mir.<group>"]` 1 행.
"""
from .agents import AgentRegistry
from .base import EntryPointRegistry
from .embedding_backends import EmbeddingBackendRegistry
from .providers import ProviderRegistry
from .skills import SkillRegistry

__all__ = [
    "AgentRegistry",
    "EmbeddingBackendRegistry",
    "EntryPointRegistry",
    "ProviderRegistry",
    "SkillRegistry",
]
