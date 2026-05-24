from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from tools.run_orchestrator.state_machine import (
    InvalidRunTransitionError,
    RunState,
)


class InterruptError(Exception):
    """Raised when interrupt-related operation fails (snapshot/restore)."""


@dataclass(frozen=True)
class Snapshot:
    """Result of a pre-ACT snapshot."""
    method: str
    ref: str
    repo_root: Path


def _run_git(*args: str, cwd=None, check: bool = True):
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )


def find_repo_root(start=None):
    """Walk up from start (or cwd) looking for .git directory."""
    start = (start or Path.cwd()).resolve()
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise InterruptError(f"not inside a git repository (started from {start})")


def take_snapshot(method: str = "stash", cwd=None, label: str = "mir-interrupt-snapshot"):
    """Snapshot current working tree state."""
    repo_root = find_repo_root(cwd)

    if method == "stash":
        result = _run_git(
            "stash", "push", "--include-untracked", "--message", label,
            cwd=repo_root, check=False,
        )
        if "No local changes to save" in (result.stdout + result.stderr):
            return Snapshot(method="stash", ref="", repo_root=repo_root)
        if result.returncode != 0:
            raise InterruptError(f"git stash failed: {result.stderr.strip()}")
        return Snapshot(method="stash", ref="stash@{0}", repo_root=repo_root)

    elif method == "worktree":
        raise NotImplementedError("worktree method is reserved for R19+ parallel ACT support")

    else:
        raise InterruptError(f"unknown snapshot method: {method}")


def restore_snapshot(snap):
    """Restore working tree from snapshot. No-op if snap.ref is empty."""
    if not snap.ref:
        return

    if snap.method == "stash":
        result = _run_git(
            "stash", "pop", snap.ref,
            cwd=snap.repo_root, check=False,
        )
        if result.returncode != 0:
            raise InterruptError(f"git stash pop failed: {result.stderr.strip()}")

    elif snap.method == "worktree":
        raise NotImplementedError("worktree method is R19+ work")


def handle_interrupt(current_state, snapshot, transition_fn):
    """Drive ACT -> CANCELLING -> ROLLBACK -> INTERRUPTED transitions."""
    if current_state not in {RunState.ACT, RunState.NEED_APPROVAL}:
        raise InvalidRunTransitionError(
            f"cannot interrupt from {current_state} — "
            "interrupt requires ACT or NEED_APPROVAL state"
        )

    transition_fn(RunState.CANCELLING)
    transition_fn(RunState.ROLLBACK)

    if snapshot is not None:
        try:
            restore_snapshot(snapshot)
        except InterruptError as e:
            print(f"[mir INTERRUPT] restore failed: {e}", file=sys.stderr)

    transition_fn(RunState.INTERRUPTED)

    return RunState.INTERRUPTED
