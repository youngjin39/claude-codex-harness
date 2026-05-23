"""Test that all markdown internal links resolve to existing files."""
import re
from pathlib import Path


def test_all_links_resolve():
    md_files = list(Path("docs").rglob("*.md")) if Path("docs").exists() else []
    if Path("applications").exists():
        md_files += list(Path("applications").rglob("*.md"))

    pattern = re.compile(r'\[.*?\]\(([^)]+)\)')
    broken = []
    for md in md_files:
        content = md.read_text()
        for match in pattern.finditer(content):
            link = match.group(1).split("#")[0].strip()
            if not link:
                continue
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            target = (md.parent / link).resolve()
            if not target.exists():
                broken.append((str(md), link))
    assert not broken, f"Broken links: {broken[:10]}"


if __name__ == "__main__":
    test_all_links_resolve()
    print("test_link_integrity: PASS")
