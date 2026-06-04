from __future__ import annotations

import json
from pathlib import Path

from tools.harness_consistency.models import Finding, summarize
from tools.harness_consistency.rules import RULES


def _manifest_path(project_root: Path, manifest_path: Path | None = None) -> Path:
    if manifest_path is None:
        return project_root / "config" / "harness-consistency.json"
    if manifest_path.is_absolute():
        return manifest_path
    return project_root / manifest_path


def load_manifest(project_root: Path, manifest_path: Path | None = None) -> dict:
    path = _manifest_path(project_root, manifest_path)
    return json.loads(path.read_text(encoding="utf-8"))


def run_with_manifest(project_root: Path, manifest: dict) -> dict:
    rule_inputs = manifest.get("rule_inputs", {})
    findings: list[Finding] = []

    for rule in manifest["rules"]:
        if not rule.get("enabled"):
            continue

        rule_name = rule["name"]
        rule_fn = RULES.get(rule_name)
        if rule_fn is None:
            findings.append(
                Finding(
                    rule_id=rule["id"],
                    rule_name=rule_name,
                    severity="ERROR",
                    message=f"Rule not implemented: {rule_name}",
                    drift_class=rule.get("drift_class"),
                )
            )
            continue

        try:
            rule_findings = rule_fn(project_root, rule_inputs.get(rule_name, {}))
        except Exception as exc:
            findings.append(
                Finding(
                    rule_id=rule["id"],
                    rule_name=rule_name,
                    severity="ERROR",
                    message=f"Rule raised {exc.__class__.__name__}: {exc}",
                    drift_class=rule.get("drift_class"),
                )
            )
            continue

        for finding in rule_findings:
            finding.severity = rule["severity"]
            if "drift_class" in rule:
                finding.drift_class = rule["drift_class"]
            findings.append(finding)

    summary = summarize(findings)
    return {
        "repo": manifest["repo"],
        "findings": [finding.to_dict() for finding in findings],
        "summary": summary,
        "overall": "pass" if summary["error"] == 0 else "fail",
    }


def run(project_root: Path, manifest_path: Path | None = None) -> dict:
    manifest = load_manifest(project_root, manifest_path)
    return run_with_manifest(project_root, manifest)
