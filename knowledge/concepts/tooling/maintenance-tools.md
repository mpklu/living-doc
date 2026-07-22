---
title: Maintenance tools — check-links, build-index, bump-updated, sweep-report, roll-log
description: "The local maintenance suite: link checking, index generation from frontmatter, updated:-date bumping, drift-sweep worklists, and log rotation — five stdlib-only tools sharing the validate_articles frontmatter parser"
type: concept
area: tooling
updated: 2026-07-22
status: thin
affects:
  - 'actions/drift-check/check_links.py'
  - 'actions/drift-check/build_index.py'
  - 'actions/drift-check/bump_updated.py'
  - 'actions/drift-check/sweep_report.py'
  - 'actions/drift-check/roll_log.py'
  - 'scripts/check-links'
  - 'scripts/build-index'
  - 'scripts/bump-updated'
  - 'scripts/sweep-report'
  - 'scripts/roll-log'
load_bearing: false
references:
  - concepts/methodology/scripts-over-reasoning.md
  - concepts/tooling/validate-articles.md
---

# Maintenance tools

Five local tools that mechanize the recurring upkeep a knowledge base
needs as it grows. All five came out of one field adoption (a ~100-article
production knowledge hub) where each had been done by hand — or worse, by
an AI agent burning reasoning on a string comparison — often enough to
hurt. The principle they implement: [[scripts-over-reasoning]].

House conventions (shared with `drift_check.py` / `validate_articles.py`):
stdlib-only Python, implementation co-located in `actions/drift-check/`
(they reuse `validate_articles.parse_frontmatter`, the shared hand-parser),
thin `cli_main(argv)` wrappers in `scripts/`, human-readable output by
default with `--json` where a machine consumer is plausible, exit 1 on
failure so every tool is CI-able.

## The tools

| Tool | Job | Failure it prevents |
| --- | --- | --- |
| `check-links` | Verify `[[wikilinks]]` (unique-stem or path-suffix resolution) and relative markdown links resolve; code fences/inline code excluded; ambiguous wikilinks are errors too | Renamed/deleted files leaving silent dangling references |
| `build-index` | Regenerate `index.md` article tables from frontmatter inside `<!-- build-index:begin dir=… -->` markers; `description:` fills "Covers" (falls back to `title:`); `--check` for CI | Hand-maintained index rows drifting from article frontmatter |
| `bump-updated` | Set `updated:` to today on given/`--staged` articles; `--check` mode for pre-commit | Forgotten date bumps silently corrupting drift-sweep ordering |
| `sweep-report` | The N oldest articles by `updated:` (optional `--area`), i.e. the drift-sweep worklist, generated not reasoned | Sweep sessions spending effort finding what to sweep instead of sweeping |
| `roll-log` | Move log entries older than the keep-window into monthly `knowledge/log/YYYY-MM.md` archives; **conservation-checked** (aborts if any entry text would be lost); preserves the active log's own entry order (newest-first and oldest-first both supported) | An unboundedly growing active log; entries lost during manual archiving |

## Design notes

- **`build-index` markers, not whole-file generation.** The index keeps
  hand-written prose; only the marked table blocks regenerate. Adopting is
  incremental — wrap one table, leave the rest.
- **`description:` is the new (optional) frontmatter field** backing
  `build-index` — see the schema. It doubles as the retrieval hook an
  agent reads to decide relevance without opening the article.
- **`bump-updated` deliberately skips** `index.md` / `log.md` and any file
  without an `updated:` line — it can be pointed at a whole staged set
  safely.
- **`roll-log`'s conservation check** re-parses everything after writing
  and compares entry-text sets; a mismatch aborts with instructions to
  restore from git. This is the property that makes automated archiving
  trustworthy.
- **`check-links` treats ambiguity as failure**: a `[[name]]` matching two
  articles is unreliable navigation even though it "resolves."

## Caveats

- `check-links` does not verify anchors (`#section`) within resolved
  files, and its inline-code masking is line-based (a multi-line
  code span could mask imperfectly).
- `build-index` sorts rows by filename; if an area wants curated ordering,
  keep that table hand-written (no marker) — the tool only owns marked
  blocks.
- `bump-updated --staged` reads the staged *name list* but edits working
  files; re-stage after it runs (the `--check` hook mode exists to make
  the workflow explicit rather than mutating during a commit).
