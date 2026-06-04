"""ARCHITECTURE.md harness contract extractor (phase-0).

Parses ARCHITECTURE.md (project root) and extracts structured
harness contract specs:
 - Required directories
 - Required files (with optional content patterns)
 - Required sections in CLAUDE.md / AGENTS.md
 - Constraints (e.g. no Hangul in template)

Output dict structure:
{
  "required_dirs": ["tasks/", "config/", ...],
  "required_files": {"CLAUDE.md": {"min_lines": 30, "required_sections": [...]}},
  "constraints": [{"target": "template_repo", "type": "no_hangul"}, ...],
  "metadata": {"source": "ARCHITECTURE.md", "extracted_at": "..."},
}
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARCHITECTURE_PATH = PROJECT_ROOT / "ARCHITECTURE.md"


def extract_contract(arch_path: Path | None = None) -> dict:
    """Parse ARCHITECTURE.md and return contract dict.

    If file absent, returns empty contract + metadata note.
    """
    path = arch_path or DEFAULT_ARCHITECTURE_PATH
    contract: dict = {
        "required_dirs": [],
        "required_files": {},
        "constraints": [],
        "metadata": {
            "source": str(path),
            "extracted_at": datetime.now(UTC).isoformat(),
            "found": path.exists(),
        },
    }
    if not path.exists():
        contract["metadata"]["error"] = "ARCHITECTURE.md not found"
        return contract

    content = path.read_text(encoding="utf-8", errors="replace")

    contract["required_dirs"] = _extract_required_dirs(content)
    contract["required_files"] = _extract_required_files(content)
    contract["constraints"] = _extract_constraints(content)

    return contract


def _extract_required_dirs(content: str) -> list[str]:
    """Extract directory references from markdown.

    Heuristic: look for list items referencing paths ending in /.
    """
    dirs: set[str] = set()
    for match in re.finditer(
        r'^[-*]\s+`?([a-zA-Z_.][a-zA-Z0-9_.-]*/[a-zA-Z0-9_./-]*)`?',
        content,
        re.M,
    ):
        token = match.group(1)
        if token.endswith("/"):
            dirs.add(token)
    for match in re.finditer(
        r'^`?([a-zA-Z_.][a-zA-Z0-9_.-]*/)`?\s*[-#]',
        content,
        re.M,
    ):
        dirs.add(match.group(1))
    return sorted(dirs)


def _extract_required_files(content: str) -> dict[str, dict]:
    """Extract file references with optional metadata."""
    files: dict[str, dict] = {}
    # Match explicit backtick-quoted filenames like `CLAUDE.md` or `.claude/settings.json`
    for match in re.finditer(
        r"`([A-Z][A-Z_]*\.md|\.[a-z]+/[a-zA-Z_]+\.[a-z]+)`",
        content,
    ):
        fname = match.group(1)
        if fname not in files:
            files[fname] = {"required": True}
    # Baseline well-known files if mentioned anywhere
    for f in ["CLAUDE.md", "AGENTS.md", "README.md", "pyproject.toml"]:
        if f in content:
            files.setdefault(f, {"required": True})
    return files


def _extract_constraints(content: str) -> list[dict]:
    """Extract constraint rules from text.

    Heuristic patterns:
    - Korean / hangul mention with absence signal -> no_hangul constraint
    - Python version mention -> python_compat constraint
    """
    constraints: list[dict] = []
    lowered = content.lower()
    if "korean" in lowered and (
        " 0" in content or "no hangul" in lowered or "absent" in lowered
    ):
        constraints.append(
            {"type": "no_hangul", "target": "template", "source": "ARCHITECTURE.md"}
        )
    if "python 3.11" in lowered or "python 3.9" in lowered:
        constraints.append(
            {"type": "python_compat", "target": "scripts/", "value": "3.11+"}
        )
    return constraints
