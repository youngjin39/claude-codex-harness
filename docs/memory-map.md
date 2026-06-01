---
title: Memory map — keyword index
description: DB-canonical memory. The keyword index is a generated projection of .mir/memory.db.
---

# Memory map

> Long-term memory is **DB-canonical** (`.mir/memory.db`, SQLite + FTS5 + sqlite-vec).
> The keyword index below is a **generated projection** inside the `mir:generated` markers — never hand-edit it.
> Frontmatter required on every memory doc: title, keywords, related, created, last_used.

## Search protocol

1. Query the DB: `mir memory query <keyword>` (FTS5), or scan the generated index below.
2. Read only matched files.
3. If a file has a `related` field, consider loading related files too.
4. No match → skip — do not load the entire docs/ tree.

## Save protocol

1. Create memory file: `docs/<category>/<topic>.md` with frontmatter:
   ```yaml
   ---
   title: {title}
   keywords: [keyword1, keyword2, ...]
   related: [other-file.md, ...]
   created: {YYYY-MM-DD}
   last_used: {YYYY-MM-DD}
   ---
   ```
2. Ingest into the DB: `mir memory ingest-md docs/<category>/<topic>.md` (deterministic frontmatter → facts; no LLM).
3. Regenerate the index: `mir memory render --target memory-map --apply --output-path docs/memory-map.md`.
4. The keyword index below is **DB-generated** — do not hand-edit it; re-ingest + re-render instead.

## Promotion

- Pattern fires twice → capture a lesson in the DB: `mir memory insert --predicate lesson --subject <slug> --object "<rule>"`, then `mir memory render --target lessons --apply --output-path tasks/lessons.md`.

<!-- mir:generated:start -->
## Keyword → File Index (DB projection)

| Keyword | File | Title |
|---|---|---|
| (no ingested documents) | — | — |
<!-- mir:generated:end -->
