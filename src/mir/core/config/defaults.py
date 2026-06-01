"""Default values — **single source**. 타 모듈은 이 상수를 직접 참조하거나 `ResolvedConfig` 경유.

design §9.6 · §9.6.3 · §9.6.4 · §9.6.5 · §7.5.
원칙:
- 이 파일 바깥에서 기본값 literal 정의 금지.
- 신규 기본값 추가 시 이 파일 + `ResolvedConfig` 필드 동시 갱신.
"""
from __future__ import annotations

# v0.5.3 R1: 자가-변조 차단 경로 (PolicyStore.denied_paths 기본값)
DEFAULT_DENIED_PATHS: tuple[str, ...] = (
    "core/**",
    ".claude/hooks/**",
    ".mir/**",
    "harness_*.toml",
    "guides.toml",
    "pyproject.toml",
    "core/registry/**",
)

# v0.5.3 R8: Worker CLI 에 상속 금지할 env var prefix. v0.5.4-6 에서 HOME 이동.
DEFAULT_DENIED_ENV_PREFIXES: tuple[str, ...] = (
    "AWS_", "GOOGLE_", "GCP_", "AZURE_",
    "OPENAI_", "ANTHROPIC_", "GEMINI_", "COHERE_", "HUGGINGFACE_",
    "SLACK_", "DISCORD_", "TELEGRAM_",
    "NPM_", "NODE_AUTH_", "PYPI_", "CARGO_",
    "GITHUB_", "GITLAB_", "BITBUCKET_",
    "SSH_", "GPG_", "AGE_",
    "MIR_SIGNING", "MIR_USER_PUBKEY",
)

# v0.5.3 R8 + v0.5.4-6: 이름으로 차단 (HOME 은 반드시 `user_home` 으로 치환 주입).
DEFAULT_DENIED_ENV_KEYS: frozenset[str] = frozenset({
    "PATH",                     # sanitize 된 최소 PATH 만 주입
    "HOME",                     # v0.5.4-6: user_home 으로 강제 치환
    "LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "DYLD_FORCE_FLAT_NAMESPACE",
    "PYTHONPATH", "PYTHONSTARTUP",
    "BASH_ENV", "ENV",
    "HISTFILE", "HISTFILESIZE",
})

# Meta approval sensitive TOML keys (v0.5.3 R8 확장).
# 이 키들이 포함된 diff 는 `allows_sensitive=true` 플래그 + 별도 승인 필요.
SENSITIVE_KEYS: frozenset[tuple[str, ...]] = frozenset({
    ("conductor", "model"),
    ("harness_b", "hooks"),
    ("mcp", "allowlist"),
    ("audit", "signer_mode"),
    ("audit", "anchor"),                # v0.5.3 R6
    ("providers", "allowlist"),         # v0.5.3 R7
    ("memory", "embedding"),            # D1 교체
    ("roles",),                         # 모든 role mapping
    ("mir", "signing_key_path"),
})

# --- Default config values (load_config 가 TOML 오버라이드 전 베이스) ---

DEFAULT_EMBEDDING_BASE_URL = "http://127.0.0.1:8001/v1"
DEFAULT_EMBEDDING_MODEL = "bge-m3-mlx-fp16"           # HF: mlx-community/bge-m3-mlx-fp16 (v0.5.4-1)
DEFAULT_EMBEDDING_DIM = 1024
DEFAULT_EMBEDDING_TIMEOUT_SEC = 10
DEFAULT_EMBEDDING_NORM_TOLERANCE = 1e-3               # v0.5.3 R3
DEFAULT_EMBEDDING_API_KEY_ENV = "OMLX_API_KEY"        # v0.5.4-2

DEFAULT_CLAUDE_MEMORY_PLUGIN_MODE = "disabled"        # v0.5.5 errata E8
DEFAULT_CLAUDE_MEMORY_RECALL_POLICY = "progressive"   # v0.5.5-1 §9.18.2

DEFAULT_CODEX_FALLBACK = "claude_n_session"           # v0.5.3 A6

# Circuit breaker (llm-circuit vendored · v0.5.3 R12)
DEFAULT_BREAKER_CONSECUTIVE_THRESHOLD = 3
DEFAULT_BREAKER_WINDOW_SIZE = 20
DEFAULT_BREAKER_WINDOW_FAILURE_RATE = 0.5
DEFAULT_BREAKER_RECOVERY_TIMEOUT = 30
DEFAULT_BREAKER_HALF_OPEN_REQUIRED_SUCCESSES = 3      # v0.5.3 R12

# Hook #3 mode (v0.5.3 R1 분리)
DEFAULT_HOOK3_SHELL_MODE = "enforce"
DEFAULT_HOOK3_AST_MODE = "advisory"

# Meta FSM transition lock (v0.5.3 H11)
DEFAULT_META_TRANSITION_STALE_SEC = 600               # 10 min
DEFAULT_NUKE_META_APPLYING_WAIT_SEC = 60              # v0.5.3 H12

# Minimal PATH injected into Worker subprocess
DEFAULT_WORKER_PATH = "/usr/bin:/bin:/opt/homebrew/bin"
