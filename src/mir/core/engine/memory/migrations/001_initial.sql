-- Migration 001 — claude_memory initial schema (MIT) + Mir minor extensions.
-- BORROWED-FROM: codenamev/claude_memory@d0e523cd06d6adeae4744d89736f79564d9db41d db/migrations/001_create_initial_schema.rb
-- design §5.1 (core memory tables).

CREATE TABLE content_items (
  id              INTEGER PRIMARY KEY,
  source          TEXT NOT NULL,
  session_id      TEXT,
  transcript_path TEXT,
  occurred_at     TEXT,
  ingested_at     TEXT,
  text_hash       TEXT,
  byte_len        INTEGER,
  raw_text        TEXT,
  metadata_json   TEXT
);

CREATE TABLE delta_cursors (
  session_id       TEXT NOT NULL,
  transcript_path  TEXT NOT NULL,
  last_byte_offset INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (session_id, transcript_path)
);

CREATE TABLE entities (
  id             INTEGER PRIMARY KEY,
  type           TEXT,
  canonical_name TEXT,
  slug           TEXT NOT NULL UNIQUE
);

CREATE TABLE entity_aliases (
  entity_id INTEGER NOT NULL REFERENCES entities(id),
  alias     TEXT NOT NULL,
  PRIMARY KEY (entity_id, alias)
);

-- facts already split per v0.5.1 Gap 4 (hot counters → fact_stats in 002).
CREATE TABLE facts (
  id                 INTEGER PRIMARY KEY,
  subject_entity_id  INTEGER,
  predicate          TEXT,
  object_entity_id   INTEGER,
  object_literal     TEXT,
  polarity           TEXT,                        -- 'asserted' | 'negated'
  valid_from         TEXT,
  valid_to           TEXT,
  status             TEXT,                        -- 'active' | 'superseded' | 'rejected'
  confidence         REAL,
  created_from       INTEGER REFERENCES content_items(id),
  scope              TEXT DEFAULT 'global',       -- 'global' | 'project'
  project_path       TEXT,
  vec_indexed_at     TEXT
);

CREATE TABLE provenance (
  fact_id               INTEGER NOT NULL REFERENCES facts(id),
  content_item_id       INTEGER REFERENCES content_items(id),
  quote                 TEXT,
  attribution_entity_id INTEGER REFERENCES entities(id),
  strength              TEXT                      -- 'stated' | 'inferred'
);

CREATE TABLE fact_links (
  from_fact_id INTEGER NOT NULL REFERENCES facts(id),
  to_fact_id   INTEGER NOT NULL REFERENCES facts(id),
  link_type    TEXT,
  PRIMARY KEY (from_fact_id, to_fact_id, link_type)
);

CREATE TABLE conflicts (
  id          INTEGER PRIMARY KEY,
  fact_a_id   INTEGER NOT NULL REFERENCES facts(id),
  fact_b_id   INTEGER NOT NULL REFERENCES facts(id),
  status      TEXT,
  detected_at TEXT,
  notes       TEXT
);

CREATE TABLE tool_calls (
  id              INTEGER PRIMARY KEY,
  content_item_id INTEGER REFERENCES content_items(id),
  tool_name       TEXT NOT NULL,
  tool_input      TEXT,
  tool_result     TEXT,
  is_error        INTEGER DEFAULT 0,
  timestamp       TEXT NOT NULL,
  gate_status     TEXT,                           -- 'ok' | 'blocked' | 'error'
  gate_rule_id    TEXT,
  gate_reason     TEXT
);
