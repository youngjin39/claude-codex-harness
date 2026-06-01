-- Migration 016 — mir_sign_consumed_nonces (RH1, v0.6.2 Independent Review).
-- decisions/v0.6.2-independent-review.md · decisions/adr-03-phase-gate-policy.md §2.2.1
--
-- Phase completion tokens carry a hex-32 nonce that must be consumed at
-- most once. The earlier design relied on an in-memory Python set that
-- was never actually threaded through to the check site — replay was
-- possible for the full 24h TTL. This table backs a ``consume_and_record``
-- single-transaction insert (same pattern as meta FSM nonces, v0.5 §2-D).
--
-- On duplicate nonce, sqlite raises IntegrityError; the check treats it
-- as ``satisfied=False`` and surfaces ``phase_gate_cfg_error`` /
-- ``phase_gate_unmet`` via the standard Hook #3 code path.

CREATE TABLE mir_sign_consumed_nonces (
  nonce        TEXT PRIMARY KEY,
  consumed_at  TEXT NOT NULL,
  phase_id     TEXT NOT NULL,
  family_id    TEXT NOT NULL,
  instance_id  TEXT
);

CREATE INDEX idx_mir_sign_nonces_consumed_at
  ON mir_sign_consumed_nonces (consumed_at);
