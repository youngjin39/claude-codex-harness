-- Migration 002 — metaswarm additions. design §5.1.
-- Hot counters split off `facts` (Gap 4). Tags + affected files as junctions.

CREATE TABLE fact_stats (
  fact_id          INTEGER PRIMARY KEY REFERENCES facts(id),
  usage_count      INTEGER NOT NULL DEFAULT 0,
  helpful_count    INTEGER NOT NULL DEFAULT 0,
  outdated_reports INTEGER NOT NULL DEFAULT 0,
  last_used_at     TEXT
);

CREATE TABLE fact_tags (
  fact_id INTEGER NOT NULL REFERENCES facts(id),
  tag     TEXT NOT NULL,
  PRIMARY KEY (fact_id, tag)
);

CREATE TABLE fact_affected_files (
  fact_id   INTEGER NOT NULL REFERENCES facts(id),
  file_path TEXT NOT NULL,
  PRIMARY KEY (fact_id, file_path)
);
