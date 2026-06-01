-- Migration 004 — hot-path indexes + FTS5 virtual table.
-- design §5.4 (indexes + PRAGMA) + §9.9 (FTS5 default).
-- vec0 virtual table lives in store.py (needs sqlite-vec extension loaded at
-- connect time; we create it conditionally, not via a static migration).

CREATE INDEX idx_facts_scope           ON facts (scope, project_path, status);
CREATE INDEX idx_facts_subject         ON facts (subject_entity_id);
CREATE INDEX idx_facts_predicate       ON facts (predicate);
CREATE INDEX idx_tool_calls_session    ON tool_calls (content_item_id, timestamp);
CREATE INDEX idx_tasks_session         ON tasks (session_id, status);
CREATE INDEX idx_reviews_task          ON reviews (task_id, verdict);
CREATE INDEX idx_circuit_state_tool    ON circuit_state (tool_name);
CREATE INDEX idx_conductor_mode_timeout ON conductor_mode (timeout_at);
CREATE INDEX idx_sessions_uuid         ON sessions (uuid);
CREATE INDEX idx_audit_log_ts          ON audit_log (ts);

-- FTS5 content-shadowed by `facts`. We index the literal body so keyword
-- queries (`mir memory query <kw>`) work even when embeddings are absent.
CREATE VIRTUAL TABLE facts_fts USING fts5(
  predicate,
  object_literal,
  content='facts',
  content_rowid='id',
  tokenize = 'unicode61'
);

-- FTS5 sync triggers — keep the shadow index in step with `facts`.
CREATE TRIGGER facts_fts_ai AFTER INSERT ON facts BEGIN
  INSERT INTO facts_fts(rowid, predicate, object_literal)
  VALUES (new.id, new.predicate, new.object_literal);
END;

CREATE TRIGGER facts_fts_ad AFTER DELETE ON facts BEGIN
  INSERT INTO facts_fts(facts_fts, rowid, predicate, object_literal)
  VALUES ('delete', old.id, old.predicate, old.object_literal);
END;

CREATE TRIGGER facts_fts_au AFTER UPDATE ON facts BEGIN
  INSERT INTO facts_fts(facts_fts, rowid, predicate, object_literal)
  VALUES ('delete', old.id, old.predicate, old.object_literal);
  INSERT INTO facts_fts(rowid, predicate, object_literal)
  VALUES (new.id, new.predicate, new.object_literal);
END;
