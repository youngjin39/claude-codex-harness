from __future__ import annotations

from dataclasses import dataclass

SEVERITIES = ("ERROR", "WARN", "INFO")


@dataclass
class Finding:
    rule_id: str
    rule_name: str
    severity: str  # ERROR | WARN | INFO
    message: str
    location: str = ""
    drift_class: int | None = None

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity,
            "message": self.message,
            "location": self.location,
            "drift_class": self.drift_class,
        }


def summarize(findings: list[Finding]) -> dict:
    return {
        "total": len(findings),
        "error": sum(1 for f in findings if f.severity == "ERROR"),
        "warn": sum(1 for f in findings if f.severity == "WARN"),
        "info": sum(1 for f in findings if f.severity == "INFO"),
    }
