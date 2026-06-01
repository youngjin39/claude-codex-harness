"""Shared helpers for CLI subcommands."""
from __future__ import annotations

from pathlib import Path

_DEFAULT_DB_RELATIVE = ".mir/memory.db"


def default_db_path(project_root: Path | None = None) -> Path:
    """`<project_root>/.mir/memory.db` — single source of default location."""
    root = project_root or Path.cwd()
    return root / _DEFAULT_DB_RELATIVE
