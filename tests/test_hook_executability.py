"""Test that all .claude/hooks/*.sh files are executable and have valid bash syntax."""
import subprocess
import stat
from pathlib import Path


def test_all_hooks_executable():
    hooks_dir = Path(".claude/hooks")
    if not hooks_dir.exists():
        return  # No hooks directory yet — pass until baseline is established
    hooks = list(hooks_dir.glob("*.sh"))
    if not hooks:
        return  # No hooks present yet
    for hook in hooks:
        mode = hook.stat().st_mode
        assert mode & stat.S_IXUSR, f"{hook} not executable (missing +x)"
        result = subprocess.run(
            ["bash", "-n", str(hook)],
            capture_output=True,
        )
        assert result.returncode == 0, (
            f"{hook} bash syntax error: {result.stderr.decode()}"
        )


if __name__ == "__main__":
    test_all_hooks_executable()
    print("test_hook_executability: PASS")
