"""AgentRegistry — `mir.agents` entry_points (AgentProfile instance factory).

design §8.4. 각 entry_point 는 `AgentProfile` 인스턴스 또는 팩토리 함수.
"""
from __future__ import annotations

from .base import EntryPointRegistry


class AgentRegistry(EntryPointRegistry):
    GROUP = "mir.agents"
