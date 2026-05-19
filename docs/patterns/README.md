# Patterns Catalogue

Transplant-ready configurations that a repository can opt into. Each pattern
records who originated it, the conditions under which it makes sense, and
what a recipient needs to adapt.

The catalogue is opt-in. A meta-harness never pushes a pattern into a
recipient repository without that repository's own commit (governance
principle 1).

## Layout

```
docs/patterns/
├── README.md                 (this file — catalogue policy)
├── INDEX.md                  (auto-generated index)
├── bounded-review-plane.md   (curriculum / docs workspaces)
├── app-product-flutter.md    (Flutter app product)
└── content-workspace.md      (narrative / score authoring)
```

## Frontmatter shape

```yaml
---
title: <pattern name>
pattern_kind: <archetype | rollout_class | hook | agent | skill | tool>
source_repository: <slug or canonical id>
license: <SPDX-id>
created: <YYYY-MM-DD>
adoption_targets:
  archetypes: [<archetype>, ...]
  management_modes: [<mode>, ...]
notes: <one-line summary>
---
```

Manual content lives between the `<!-- generated:start -->` and
`<!-- generated:end -->` markers; everything outside the marker block is
preserved on regeneration.

## Adoption workflow

1. Pick a pattern from `INDEX.md`.
2. Author an import spec referencing the source repository.
3. Run the canary apply on a single high-fit recipient.
4. If clean, fan out to remaining fits. If not, the rollback path
   restores the recipient.

Hook patterns are documentation-only: a `kind=hook` import is blocked
upstream (advisory only by governance principle 1). The pattern serves
as the reference for a recipient-owned commit.
