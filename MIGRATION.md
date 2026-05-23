# Migration Guide

This document records breaking changes between major versions of `claude-codex-harness`. Each entry covers migration steps for existing fleet adopters to upgrade.

## Format

Each section follows the pattern:

```markdown
## v<N+1>.0.0 ← v<N>.x.y

### Breaking changes
- (list of breaking changes)

### Migration steps (per family)
1. (concrete commands or edits)

### Rollback
- (procedure to revert if migration fails)
```

## Current Status

No MAJOR releases yet. Current version: `0.1.0` (initial public release). Next MAJOR (`1.0.0`) will introduce the first breaking change and gain the first section in this file.

## See Also

- [`CHANGELOG.md`](CHANGELOG.md) — non-breaking change log (PATCH/MINOR)
- [`VERSION`](VERSION) — current semver
