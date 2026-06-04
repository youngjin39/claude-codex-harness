from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_harness_consistency_zero_error_on_current_repo() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "tools.harness_consistency", "run", "--format", "json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads(proc.stdout)
    assert result["overall"] == "pass", result["summary"]
    assert result["summary"]["error"] == 0
