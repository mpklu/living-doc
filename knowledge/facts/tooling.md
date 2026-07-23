<!-- build-facts:generated — edit the articles' ## Facts sections, not this file -->

# Facts — tooling

Atomic lookup facts extracted from the `tooling` articles' `## Facts` sections by `scripts/build-facts`. One small surface for needle queries; open the linked article for the why.

## maintenance-tools — [../concepts/tooling/maintenance-tools.md](../concepts/tooling/maintenance-tools.md)

- **check-links**: `scripts/check-links [--exclude 'log/*']` — wikilinks + relative links resolve; ambiguity = error
- **build-index**: `scripts/build-index [--check]` — index tables from frontmatter, `<!-- build-index:begin dir=… -->` markers
- **bump-updated**: `scripts/bump-updated [--staged] [--check] [--date D]` — set `updated:` today
- **sweep-report**: `scripts/sweep-report [--limit N] [--area A]` — oldest articles by `updated:`; skips `log/` + `facts/`
- **roll-log**: `scripts/roll-log [--keep-days 14|--keep-since D] [--dry-run]` — monthly archives, conservation-checked
- **provenance-report**: `scripts/provenance-report [--worklist [--all]]` — tag coverage / verification worklist (corroborated `*(reported: …; code: …)*` claims are suppressed from the worklist)
- **build-facts**: `scripts/build-facts [--check]` — `knowledge/facts/<area>.md` from `## Facts` sections
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
