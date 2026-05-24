"""Mir approval gate (phase-4 §3-9 + phase-4-approval-discord-delegation.md).

Mediates NEED_APPROVAL state transitions via Discord plugin reply tool.
Does NOT call Discord directly — Claude Code's MCP plugin owns the actual
reply. This module:
  - generates the request payload (writes approval.json + returns Discord
    message text)
  - parses user replies for APPROVE/DENY/DELAY <approval_id> patterns
  - applies decisions (update approval.json + transition run_state)
"""
from __future__ import annotations

import json
import re
import secrets
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import jsonschema

from tools.run_orchestrator.run_orchestrator import (
    DEFAULT_RUN_STATE_PATH,
    get_current_state,
    transition,
)
from tools.run_orchestrator.state_machine import (
    RunState,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_APPROVAL_DIR = PROJECT_ROOT / "tasks" / "approvals"
DEFAULT_APPROVAL_SCHEMA_PATH = (
    PROJECT_ROOT / "docs" / "templates" / "_schema" / "approval.schema.json"
)


class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    DELAYED = "DELAYED"
    EXPIRED = "EXPIRED"


class ApprovalError(Exception):
    """Raised when approval operation fails."""


@dataclass(frozen=True)
class ApprovalRequest:
    """Result of request_approval — what to send to Discord."""
    approval_id: str
    run_id: str
    risk_level: str
    summary: str
    discord_text: str  # the formatted ## message
    file_path: Path


@dataclass(frozen=True)
class Decision:
    """Result of parse_reply — what user decided."""
    approval_id: str
    decision: str  # "APPROVE" | "DENY" | "DELAY"
    reason: str | None  # for DELAY or DENY


def _ulid() -> str:
    """Minimal Crockford base32 ULID (26 chars)."""
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    ts = int(time.time() * 1000)
    randpart = secrets.token_bytes(10)
    # encode 48-bit ts + 80-bit random as 26 base32 chars
    raw = ts.to_bytes(6, "big") + randpart
    bits = int.from_bytes(raw, "big")
    out = []
    for i in range(26):
        out.append(alphabet[(bits >> (5 * (25 - i))) & 0b11111])
    return "".join(out)


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _atomic_write(path: Path, content: str) -> None:
    """Atomic JSON write via tempfile + os.replace."""
    import os
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix=".json", dir=str(path.parent))
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def request_approval(
    run_id: str,
    risk_level: str,
    summary: str,
    auto_policy: dict[str, Any] | None = None,
    discord_chat_id: str | None = None,
    approval_dir: Path = DEFAULT_APPROVAL_DIR,
    approval_schema_path: Path = DEFAULT_APPROVAL_SCHEMA_PATH,
) -> ApprovalRequest:
    """Create a new approval request.

    Writes approval.json (jsonschema-validated), returns ApprovalRequest with
    Discord-ready text. Caller invokes Discord plugin reply tool with
    request.discord_text + reply_to context.
    """
    if risk_level not in {"low", "medium", "high"}:
        raise ApprovalError(f"invalid risk_level: {risk_level} (low|medium|high)")

    if auto_policy is None:
        auto_policy = {
            "on_timeout": "deny" if risk_level == "high" else "escalate",
            "timeout_minutes": 60 if risk_level == "high" else 30,
        }

    approval_id = _ulid()
    requested_at = _now_iso()

    record: dict[str, Any] = {
        "approval_id": approval_id,
        "run_id": run_id,
        "status": ApprovalStatus.PENDING.value,
        "risk_level": risk_level,
        "auto_policy": auto_policy,
        "requested_at": requested_at,
        "summary": summary,
    }
    if discord_chat_id:
        record["discord_chat_id"] = discord_chat_id

    # validate against schema
    with open(approval_schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    try:
        jsonschema.validate(record, schema)
    except jsonschema.ValidationError as e:
        raise ApprovalError(f"approval record failed schema validation: {e.message}") from e

    file_path = approval_dir / f"{approval_id}.json"
    _atomic_write(file_path, json.dumps(record, indent=2, ensure_ascii=False))

    discord_text = (
        f"## Approval Required (approval_id: `{approval_id}`)\n\n"
        f"**Run**: `{run_id}`\n"
        f"**Risk**: {risk_level}\n"
        f"**Action**: {summary}\n\n"
        f"Reply with: `APPROVE {approval_id}` | `DENY {approval_id}` | "
        f"`DELAY {approval_id} <reason>`"
    )

    return ApprovalRequest(
        approval_id=approval_id,
        run_id=run_id,
        risk_level=risk_level,
        summary=summary,
        discord_text=discord_text,
        file_path=file_path,
    )


_REPLY_PATTERN = re.compile(
    r"(?i)(?P<verb>APPROVE|DENY|DELAY)\s+(?P<id>[0-9A-HJKMNP-TV-Z]{26})(?:\s+(?P<reason>.+))?",
    re.IGNORECASE,
)


def parse_reply(text: str) -> Decision | None:
    """Parse user Discord reply for APPROVE/DENY/DELAY pattern.

    Returns Decision or None if no pattern matched.
    """
    m = _REPLY_PATTERN.search(text)
    if not m:
        return None
    return Decision(
        approval_id=m.group("id"),
        decision=m.group("verb").upper(),
        reason=m.group("reason"),
    )


def load_approval(approval_id: str,
                  approval_dir: Path = DEFAULT_APPROVAL_DIR) -> dict[str, Any]:
    """Load approval record from disk. Raises ApprovalError if not found."""
    path = approval_dir / f"{approval_id}.json"
    if not path.exists():
        raise ApprovalError(f"approval {approval_id} not found at {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_decision(
    decision: Decision,
    run_state_path: Path = DEFAULT_RUN_STATE_PATH,
    approval_dir: Path = DEFAULT_APPROVAL_DIR,
) -> dict[str, Any]:
    """Apply a Decision to the approval record + run_state.

    APPROVE -> approval.status=APPROVED, run NEED_APPROVAL -> ACT
    DENY    -> approval.status=DENIED, run NEED_APPROVAL -> CANCELLING
    DELAY   -> approval.status=DELAYED, run NEED_APPROVAL -> CANCELLING
              (blocked_reason="user delayed: <reason>", best effort without SM BLOCKED)
    """
    record = load_approval(decision.approval_id, approval_dir)
    if record["status"] != ApprovalStatus.PENDING.value:
        raise ApprovalError(
            f"approval {decision.approval_id} already in status "
            f"{record['status']}, cannot apply {decision.decision}"
        )

    current = get_current_state(run_state_path)
    if current != RunState.NEED_APPROVAL:
        raise ApprovalError(
            f"run not in NEED_APPROVAL (current: {current}), "
            f"cannot apply {decision.decision}"
        )

    decided_at = _now_iso()
    record["decided_at"] = decided_at
    if decision.decision == "APPROVE":
        record["status"] = ApprovalStatus.APPROVED.value
        transition(
            RunState.ACT,
            path=run_state_path,
            approval_id=decision.approval_id,
            current_lane='codex',
        )
    elif decision.decision == "DENY":
        record["status"] = ApprovalStatus.DENIED.value
        if decision.reason:
            record["denial_reason"] = decision.reason
        transition(RunState.CANCELLING, path=run_state_path,
                   approval_id=decision.approval_id)
    elif decision.decision == "DELAY":
        record["status"] = ApprovalStatus.DELAYED.value
        reason = decision.reason or "user delay (no reason)"
        record["delay_reason"] = reason
        transition(RunState.CANCELLING, path=run_state_path,
                   approval_id=decision.approval_id)
    else:
        raise ApprovalError(f"unknown decision: {decision.decision}")

    file_path = approval_dir / f"{decision.approval_id}.json"
    _atomic_write(file_path, json.dumps(record, indent=2, ensure_ascii=False))

    return record
