"""ADR-09 Phase 9A -- agent_loader CLI.

Usage:
    python -m tools.agent_loader <path> [--mode=lenient|strict]

Exit codes:
    0 -- frontmatter valid.
    1 -- validation error (errors printed to stderr).
    2 -- file not found or parse error.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .loader import AgentValidationError, load_agent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.agent_loader",
        description="Validate agent frontmatter against ADR-09 schema.",
    )
    parser.add_argument("path", help="Path to .claude/agents/<agent>.md")
    parser.add_argument(
        "--mode",
        choices=["lenient", "strict"],
        default="lenient",
        help=(
            "lenient (default, Phase 9A): execution_backend may be absent. "
            "strict (Phase 9B+): execution_backend required."
        ),
    )
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    try:
        spec = load_agent(path, mode=args.mode)
    except AgentValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"error: {path}: {exc}", file=sys.stderr)
        return 2

    print(
        f"valid: name={spec.name} model={spec.model} "
        f"execution_backend={spec.execution_backend or '<absent>'} "
        f"mode={args.mode}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
