"""Module entry -- `python -m tools.agent_loader` dispatches to cli.main."""

from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
