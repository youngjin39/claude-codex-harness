#!/bin/bash
# pre-commit-verification.sh — template repo lint chain wrapper (ci.md §2-1)
# Checks: schema validity, link integrity, no Korean in user-facing files.
# Exit 0 = all checks pass; non-zero = at least one check failed.
set -e

python tests/test_schema_validity.py
python tests/test_link_integrity.py
python tests/test_no_korean_in_user_facing.py
echo "[template pre-commit] PASS"
