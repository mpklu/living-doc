---
title: affects globs — code↔article mapping
type: concept
area: methodology
updated: 2026-04-29
status: thin
---

# `affects:` globs

Each article declares which code paths it covers via an `affects:` list
of globs in its frontmatter. Articles are the source of truth for *what
they cover*; the CLAUDE.md mapping table becomes a generated artifact
(or disappears).

## How it works

Frontmatter:

```yaml
affects:
  - 'src/skills/mp-catalog/**'
  - 'scripts/refresh-catalog*'
  - 'scripts/enrich-bundle*'
```

The drift checker walks `knowledge/**.md`, reads each article's
`affects:`, and builds the code-path → article(s) map dynamically.
Pre-commit and PR-time checks both consume the same map. The CLAUDE.md
table — if present — can be either:

- **Generated** by `scripts/gen-mapping` (run as a pre-commit hook or
  documentation step) for human readability.
- **Removed** from CLAUDE.md entirely, with a pointer to "see
  `knowledge/index.md` for the article list."

Either way, hand-edits to the table stop being load-bearing. The
articles are.

## Why globs

Three alternatives considered, ruled out:

- **Free-text patterns** ("the LLM agent code") — the current
  drift_check.py fallback. Brittle: keyword matching against file
  paths produces false positives ("agent" in `src/management/agent_lifecycle.py`
  triggers an article about LLM agents). Globs are unambiguous.
- **Explicit file lists** — too much maintenance burden as files move.
- **Path prefixes** — too coarse. A glob can express "everything
  matching `src/skills/mp-catalog/**` AND `scripts/refresh-catalog*`"
  in one declaration; prefixes can't.

Globs are middle-ground: precise enough to avoid false positives,
flexible enough that file moves within a directory don't break them.

## Backward compatibility

Adopters with existing hand-edited mapping tables don't need to
migrate immediately. The drift checker's behaviour:

1. Scan articles for `affects:` frontmatter. Build map A.
2. Parse the CLAUDE.md mapping table (legacy). Build map B.
3. Use the union of A + B for the actual check.

Adopters can migrate incrementally: add `affects:` to articles when
they're touched anyway (per the same-task rule), let the table shrink
naturally. After enough articles have `affects:`, delete the table.

## Limitations honestly stated

- **No semantic relationships.** An article about "the catalog refresh
  pipeline" affects scripts AND the skill's catalog.json reader. Both
  must be listed. Globs can't express transitive dependencies.
- **Multi-article ownership is fine.** Two articles can claim the same
  code path; both flag for update on a change. Sometimes correct
  (cross-cutting concerns); occasionally noisy. Live with it.
- **Globs match paths, not semantics.** A refactor that moves a
  function between files in the same glob still requires article
  judgment. The check is "did you open the article?", not "did you
  write the right thing?".

## Migration of this repo's mapping

`CLAUDE.md` in this repo currently has a hand-edited table. Once the
implementing bundle ships:

1. Add `affects:` to existing articles (none today since they're all
   methodology-meta with no specific code coverage; will fill in as
   tooling articles appear).
2. The methodology articles use `affects:` for *the prose files they
   document* — e.g., `dogfooding.md` could declare
   `affects: ['CLAUDE.md', 'README.md']` since those are what the
   article protects against drift on.
3. CLAUDE.md's table either auto-regenerates or gets removed.

## Files

- `actions/drift-check/drift_check.py` — current legacy-table parser
  (will be extended to read `affects:` first, fall back to legacy)
- `frontmatter-as-source-of-truth.md` — the schema this builds on
- `local-vs-pr-enforcement.md` — where the same map is consumed
  twice (locally + CI)
