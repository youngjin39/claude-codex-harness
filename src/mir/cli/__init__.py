"""CLI entry points — `python -m mir …` dispatcher.

Trimmed for the public template: only `memory` and `migrate` subcommands
are wired here. The full subcommand set lives in the Mir private harness.

Subcommand registration is the only job here; real work lives under each
subcommand module.
"""
from __future__ import annotations

from collections.abc import Callable

from . import memory as _memory
from . import migrate as _migrate

# Registry pattern (design §0): no hard-coded ladder in __main__.
# New subcommand = 1 row here.
SUBCOMMANDS: dict[str, Callable[[list[str]], int]] = {
    'migrate': _migrate.main,
    'memory': _memory.main,
}
