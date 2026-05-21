# Adapted from harness design docs.
"""
tools.profile_compiler
======================
Profile Compiler: reads .mir/repo-profile.toml for a target family and
re-generates that family's role-policy sections in CLAUDE.md / AGENTS.md
and (in later phases) enforcement hooks + Codex spawn wrapper.

Phase P0-A: core modules only (profile_loader, markers, preserve, render).
"""

__version__ = "0.1.0"
