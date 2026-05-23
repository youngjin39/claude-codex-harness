"""Extract a single version entry from CHANGELOG.md and print it to stdout.

Usage:
    python scripts/extract_changelog_entry.py 0.1.0

Exit codes:
    0 — entry found and printed
    1 — version not found in CHANGELOG.md
"""
import re
import sys
from pathlib import Path


def extract_entry(changelog_text: str, version: str) -> str | None:
    """Return the text block for a given version, or None if not found."""
    # Matches "## [0.1.0]" or "## [0.1.0] - 2026-05-23" style headers
    pattern = re.compile(
        r"^## \[" + re.escape(version) + r"\].*?$",
        re.MULTILINE,
    )
    match = pattern.search(changelog_text)
    if not match:
        return None

    start = match.start()
    # Find the next version header (## [x.y.z]) or end of file
    next_header = re.compile(r"^## \[", re.MULTILINE)
    next_match = next_header.search(changelog_text, match.end())
    end = next_match.start() if next_match else len(changelog_text)

    return changelog_text[start:end].strip()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: extract_changelog_entry.py <VERSION>", file=sys.stderr)
        return 1

    version = sys.argv[1].lstrip("v")  # strip leading 'v' if present
    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        print(f"ERROR: {changelog_path} not found", file=sys.stderr)
        return 1

    changelog_text = changelog_path.read_text(encoding="utf-8")
    entry = extract_entry(changelog_text, version)

    if entry is None:
        print(f"ERROR: version [{version}] not found in CHANGELOG.md", file=sys.stderr)
        return 1

    print(entry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
