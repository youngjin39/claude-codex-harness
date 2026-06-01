"""EntryPointRegistry — 공통 베이스 · Python `importlib.metadata.entry_points` 기반.

design §8.4. 서브클래스는 `GROUP` 클래스 변수만 지정.
"""
from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any


class EntryPointRegistry:
    """entry_points 로드 후 name→class 매핑만 제공. 하드코딩 dict 금지."""

    GROUP: str = ""  # 서브클래스가 지정

    def __init__(self) -> None:
        if not self.GROUP:
            raise NotImplementedError(
                f"{type(self).__name__} must set `GROUP` class variable"
            )
        self._cache: dict[str, type[Any]] | None = None

    def _discover(self) -> dict[str, type[Any]]:
        if self._cache is None:
            self._cache = {ep.name: ep.load() for ep in entry_points(group=self.GROUP)}
        return self._cache

    def get(self, name: str) -> type[Any]:
        eps = self._discover()
        if name not in eps:
            raise KeyError(f"{self.GROUP}: no entry_point named {name!r}")
        return eps[name]

    def all_names(self) -> list[str]:
        return sorted(self._discover().keys())

    def has(self, name: str) -> bool:
        return name in self._discover()

    def reset(self) -> None:
        """테스트 용도: 캐시 초기화 (monkeypatch 후 재discover)."""
        self._cache = None
