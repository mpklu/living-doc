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
  - 'actions/drift-check/provenance_report.py'
  - 'scripts/provenance-report'
  - 'actions/drift-check/build_facts.py'
  - 'scripts/build-facts'
  - 'actions/drift-check/check_affects.py'
  - 'scripts/check-affects'
  - 'actions/drift-check/check_trailer.py'
  - 'scripts/check-trailer'
  - 'actions/drift-check/check_dates.py'
  - 'scripts/check-dates'
  # hooks README documents the whole tool family now, not just drift-check —
  # shared ownership with tooling/drift-check.md (multi-article ownership is fine)
  - 'templates/hooks/**'
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

## Facts

- **check-links**: `scripts/check-links [--exclude 'log/*']` — wikilinks + relative links resolve; ambiguity = error
- **build-index**: `scripts/build-index [--check]` — index tables from frontmatter, `<!-- build-index:begin dir=… -->` markers
- **bump-updated**: `scripts/bump-updated [--staged] [--check] [--date D]` — set `updated:` today
- **sweep-report**: `scripts/sweep-report [--limit N] [--area A]` — oldest articles by `updated:`; skips `log/` + `facts/`
- **roll-log**: `scripts/roll-log [--keep-days 14|--keep-since D] [--dry-run]` — monthly archives, conservation-checked
- **provenance-report**: `scripts/provenance-report [--worklist [--all]]` — tag coverage / verification worklist (corroborated `*(reported: …; code: …)*` claims are suppressed from the worklist)
- **build-facts**: `scripts/build-facts [--check]` — `knowledge/facts/<area>.md` from `## Facts` sections
- **check-affects**: `scripts/check-affects [--source-root P] [--strict]` — affects hygiene: free-text/article-tree = error; dead-glob/bare-literal = warn; `external:` exempt
- **check-trailer**: `scripts/check-trailer --knowledge-repo P [--install|--warn-only]` — PRODUCT-repo commit-msg hook: mapped changes require a `Knowledge:` trailer or `no knowledge impact:` line
- **check-dates**: `scripts/check-dates [--today D] [--strict]` — past dates still framed as future (sweep/CI-non-blocking, NOT the commit gate: findings appear because time passed)
- **Implementations**: `actions/drift-check/*.py` (shared parser); wrappers: `scripts/*` *(code: actions/drift-check/)*

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
| `check-links` | Verify `[[wikilinks]]` (unique-stem or path-suffix resolution) and relative markdown links resolve; code fences/inline code excluded; ambiguous wikilinks are errors too; `--exclude 'log/*'` skips append-only surfaces (their entries are frozen narrative — exclude, don't retro-edit; excluded files still count as link *targets*) | Renamed/deleted files leaving silent dangling references |
| `build-index` | Regenerate `index.md` article tables from frontmatter inside `<!-- build-index:begin dir=… -->` markers; `description:` fills "Covers" (falls back to `title:`); `--check` for CI | Hand-maintained index rows drifting from article frontmatter |
| `bump-updated` | Set `updated:` to today on given/`--staged` articles; `--check` mode for pre-commit | Forgotten date bumps silently corrupting drift-sweep ordering |
| `sweep-report` | The N oldest articles by `updated:` (optional `--area`), i.e. the drift-sweep worklist, generated not reasoned | Sweep sessions spending effort finding what to sweep instead of sweeping |
| `roll-log` | Move log entries older than the keep-window into monthly `knowledge/log/YYYY-MM.md` archives; **conservation-checked** (aborts if any entry text would be lost); preserves the active log's own entry order (newest-first and oldest-first both supported) | An unboundedly growing active log; entries lost during manual archiving |
| `provenance-report` | Claim-provenance tag coverage (per-article `code/bench/field/reported/inferred` counts; flags `load_bearing` articles with zero tags) and `--worklist` — every *uncorroborated* inferred/reported claim in a load-bearing article (combined-parenthetical claims like `*(reported: vendor; code: Foo.m:12)*` count as verified and are suppressed), i.e. the generated input for verification/refutation sweeps. Semantics: [[claim-provenance]] | Tags rotting into decoration; verification effort spent re-reading everything instead of targeting ungraded claims |
| `check-affects` | Lints every `affects:` entry — free text and `knowledge/**`-tree claims are errors; dead globs and dead bare literals warn (liveness vs this repo + repeatable `--source-root`); `external:`-prefixed entries exempt. Semantics: [[affects-globs]] hygiene rules | The four latent mapping bugs the commit gate's maiden run caught by trial-and-error — as a linter, before commit |
| `check-trailer` | Runs in a *product* repo (commit-msg hook via `--install`): staged paths matched against the knowledge repo's `affects:` globs (same matcher: `**`, braces, repo-basename-prefixed candidates; `external:` entries match by repo name — path-SEGMENT equality with dotted segments excluded, so a repo named after part of the GitLab host can't false-match → whole-repo mapping) — a mapped change without a `Knowledge:` trailer or `no knowledge impact:` line blocks, printing the expected article list. `--warn-only` for soft rollout; no CI net behind `--no-verify` in product repos is a documented trade-off | The same-task rule's cross-repo half riding on agent memory alone |
| `check-dates` | Flags time-bombed prose: a past date co-occurring with a future-tense marker (will/expected/retires/deadline/by then/…) on one line; ISO + month-year dates; frontmatter, code, provenance tags, dated log headings masked; `--today` time-travel for previews. Warn-only by design — findings appear because *time passed*, so it belongs in the periodic sweep and non-blocking CI, never the commit gate | A hard vendor date sitting future-tense across 4+ articles for three weeks after it passed |
| `build-facts` | Concatenates articles' `## Facts` sections per `area:` into generated `knowledge/facts/<area>.md` (sentinel first line; orphan cleanup; `--check` gate). Semantics: [[facts-register]] | Needle queries paying 20–60KB prose loads for one-line answers |

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
