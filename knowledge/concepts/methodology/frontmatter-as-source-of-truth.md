---
title: Frontmatter as source of truth
type: concept
area: methodology
updated: 2026-04-29
status: thin
---

# Frontmatter as source of truth

Article metadata (lifecycle, code coverage, criticality, cross-links)
lives in YAML frontmatter at the top of each article — not in the
CLAUDE.md mapping table, not in a sidecar index file, not in the
adoption guide's prose. The article *is* the metadata's home.

## Schema

```yaml
---
# Required
title: <human-readable>
type: concept | connection | meta
area: <project-defined; in this repo: methodology | tooling | meta>
updated: YYYY-MM-DD
status: thin | mature | deprecated

# Optional, but powerful
affects: ['glob/pattern/**', 'src/foo.ts']
load_bearing: true       # only when accuracy is critical
references: ['other-article.md']
---
```

JSON Schema lives at `schemas/article-frontmatter.schema.json`
(planned; not yet shipped).

### Field semantics

- **`type: concept`** — standalone reference for a single subject area.
  **`type: connection`** — cross-cutting article tying multiple
  concepts together. **`type: meta`** — about the documentation system
  itself.
- **`area:`** — project-defined grouping. Mira uses `mira | macpractice
  | providers`; this repo uses `methodology | tooling | meta`.
  Adopters define their own. Drives directory layout under
  `concepts/<area>/`.
- **`status: thin`** — first draft, capture-first. **`mature`** — has
  survived at least one drift sweep without contradicting code.
  **`deprecated`** — superseded; kept for history.
- **`affects:`** — list of glob patterns for code paths this article
  documents. The `affects:`-based mapping replaces hand-edited tables
  in CLAUDE.md (see `affects-globs.md`).
- **`load_bearing: true`** — accuracy is critical (auth flows, public
  APIs, config schemas). Drift checker treats these strictly; others
  leniently.
- **`references:`** — explicit cross-links. Validators can detect
  orphaned articles by walking the reference graph.

## Why frontmatter, not a table

Hand-edited mapping tables in CLAUDE.md drift silently. Three failure
modes I'd-or-have-seen:

- Article added; table forgotten. Drift check can't find the article;
  the methodology silently fails for that path.
- Code path renamed; table-row pattern becomes stale. The check passes
  spuriously because nothing matches.
- Two contributors edit the table simultaneously; merge conflict in
  CLAUDE.md the LLM may resolve incorrectly.

Co-locating metadata with its article eliminates all three: there is
exactly one place to update, and that place is the file you're already
editing.

## Why required fields are required

`title`, `type`, `area`, `updated`, `status` are the minimum the
methodology needs to function:

- `title` — humans + LLMs scanning the index need it.
- `type` + `area` — directory placement and table grouping.
- `updated` — drift sweep prioritizes oldest first.
- `status` — drift triage; `thin` articles need lighter scrutiny than
  `mature` ones because they're known to be incomplete.

## What's deferred

A small validator CLI (`scripts/validate-articles`) that checks every
file's frontmatter against the JSON Schema and flags missing fields,
unknown `area:` values, broken `references:`, etc. Lands as part of
the same-bundle work that adds `affects:` (see `affects-globs.md`).

## Files

- `schemas/article-frontmatter.schema.json` — planned, not yet shipped
- `affects-globs.md` — what becomes possible once frontmatter is
  reliable
- `templates/{brownfield,greenfield}/knowledge/concepts/example.md` —
  reference instances of the schema (planned addition to templates)
