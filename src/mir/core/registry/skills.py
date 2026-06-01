"""SkillRegistry — `mir.skills` entry_points.

design §8.4. Phase 1 은 빈 Registry (Mir 내장 skill 은 .claude/skills/ 유지).
family 고유 skill 을 entry_point 로 등록 가능한 구조.
"""
from __future__ import annotations

from .base import EntryPointRegistry


class SkillRegistry(EntryPointRegistry):
    GROUP = "mir.skills"
