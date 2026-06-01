-- Migration 014 — backfill canonical predicates for rows written before
-- `predicates.canonicalize()` was wired into distill.py.
-- BORROWED-FROM: codenamev/claude_memory@d0e523cd06d6adeae4744d89736f79564d9db41d db/migrations/014_canonicalize_predicates.rb
-- design §9.19.
--
-- Live inserts go through `predicates.canonicalize()`; this migration only
-- covers historical data. Keep in lockstep with `predicates.PREDICATE_MAP`.

UPDATE facts SET predicate = 'use'
 WHERE LOWER(TRIM(predicate)) IN ('use', 'uses', 'used', 'using');

UPDATE facts SET predicate = 'call'
 WHERE LOWER(TRIM(predicate)) IN ('call', 'calls', 'called', 'calling');

UPDATE facts SET predicate = 'depend_on'
 WHERE LOWER(TRIM(predicate)) IN ('depend on', 'depends on', 'depended on', 'depending on');

UPDATE facts SET predicate = 'import'
 WHERE LOWER(TRIM(predicate)) IN ('import', 'imports', 'imported');

UPDATE facts SET predicate = 'extend'
 WHERE LOWER(TRIM(predicate)) IN ('extend', 'extends', 'extended');

UPDATE facts SET predicate = 'implement'
 WHERE LOWER(TRIM(predicate)) IN ('implement', 'implements', 'implemented');

UPDATE facts SET predicate = 'reference'
 WHERE LOWER(TRIM(predicate)) IN ('reference', 'references', 'referenced');
