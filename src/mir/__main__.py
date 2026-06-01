"""`python -m mir <subcommand> …` — delegates to mir.cli."""
from __future__ import annotations

from mir.cli.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
