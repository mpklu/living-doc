## [2026-07-22] tooling | maintenance suite (check-links, build-index, bump-updated, sweep-report, roll-log) + `description:` field

First upstreaming of field experience from a production adoption (a
~100-article knowledge hub retrofitted over ~3 months, multi-repo product
family). The recurring upkeep that hurt there — dangling links after
renames/deletes, hand-synced index rows drifting, forgotten `updated:`
bumps corrupting sweep order, agent-scanned sweep worklists, an active
log outgrowing its readable window — is now mechanized as five
stdlib-only tools (implementations co-located with the shared
frontmatter parser in `actions/drift-check/`, thin wrappers in
`scripts/`, all CI-able via exit codes): `check-links`, `build-index`,
`bump-updated`, `sweep-report`, and `roll-log` (ported from that
adoption, where it runs in production; conservation-checked so no log
entry can be silently lost; generalized to support newest-first logs
like this repo's).

Supporting changes: optional `description:` frontmatter field
(schema + validator) as the one-line retrieval hook; this repo's own
`index.md` tables are now **generated** by `build-index`, with the ten
hand-written "Covers" summaries migrated verbatim into each article's
`description:` (single source — the index can no longer drift).
Deliberate call: the ten articles' `updated:` dates were NOT bumped
(metadata-only move; content wasn't re-verified, so their drift-sweep
priority stays honest). Hooks README gains the three companion hooks
(`bump-updated --staged --check`, `check-links`,
`build-index --check`).

Articles: `tooling/maintenance-tools.md` (the suite's internals + design
notes + caveats) and `methodology/scripts-over-reasoning.md` (the
principle: anything checkable by string/date/path comparison is a
script's job; AI reasoning is reserved for semantics — with the field
evidence). Non-mechanical field learnings parked in `ROADMAP.md` under
"Candidate refinements from field adoption (2026-07)": facts register,
hub-article type, 3-tier topology, stale-date flagger, `affects:`
liveness, cross-repo trailer hook, scaffolds, secret/PHI lint,
verify-before-write.
