"""harness_contract CLI."""

import argparse
import json
import sys
from pathlib import Path

from tools.harness_contract.detector import check_drift, summarize
from tools.harness_contract.extractor import extract_contract


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.harness_contract",
        description="Harness contract extractor and drift checker.",
    )
    parser.add_argument("subcommand", choices=["extract", "check"])
    parser.add_argument(
        "--architecture",
        type=Path,
        default=None,
        help="Path to ARCHITECTURE.md (default: project root)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root for drift check",
    )
    parser.add_argument(
        "--format",
        choices=["console", "json"],
        default="console",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write output to this file path instead of stdout",
    )
    args = parser.parse_args()

    contract = extract_contract(args.architecture)

    if args.subcommand == "extract":
        output = json.dumps(contract, indent=2, ensure_ascii=False)
        if args.report:
            args.report.write_text(output + "\n", encoding="utf-8")
        else:
            print(output)
        return 0

    # check subcommand
    project_root = args.project_root or Path(__file__).resolve().parents[2]
    findings = check_drift(contract, project_root)
    summary = summarize(findings)
    result = {"contract": contract, "findings": findings, "summary": summary}

    if args.format == "json":
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = _render_console(result)

    if args.report:
        args.report.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 0 if summary["major"] == 0 else 1


def _render_console(result: dict) -> str:
    lines = ["=== Harness Contract Drift Check ==="]
    source = result["contract"]["metadata"]["source"]
    total = result["summary"]["total"]
    major = result["summary"]["major"]
    minor = result["summary"]["minor"]
    lines.append(f"contract source: {source}")
    lines.append(f"findings: {total} (major={major}, minor={minor})")
    for finding in result["findings"]:
        marker = "x" if finding["severity"] == "major" else "!"
        target = finding["target"]
        detail = finding["detail"]
        lines.append(f"  [{marker}] {target}: {detail}")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
