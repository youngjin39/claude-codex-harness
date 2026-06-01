"""SQL migrations — discovered dynamically.

Files follow `NNN_snake_name.sql` (3-digit version prefix). The runner in
`store.py` glob-lists this package and applies pending migrations in sorted
order inside a single transaction each.

No Python code lives here — this package is a resource container.
"""
