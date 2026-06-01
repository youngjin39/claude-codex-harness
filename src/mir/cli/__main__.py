"""`python -m mir <subcommand> …`"""
from __future__ import annotations

import sys

from . import SUBCOMMANDS


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        names = ", ".join(sorted(SUBCOMMANDS))
        print(f"usage: python -m mir <subcommand> [args]\nsubcommands: {names}")
        return 0 if argv else 2
    cmd, *rest = argv
    handler = SUBCOMMANDS.get(cmd)
    if handler is None:
        print(f"unknown subcommand: {cmd!r}", file=sys.stderr)
        return 2
    return handler(rest)


if __name__ == "__main__":
    raise SystemExit(main())
