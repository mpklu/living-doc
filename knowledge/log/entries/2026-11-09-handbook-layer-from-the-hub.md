## 2026-11-09 — Optional handbook layer: current-state pages kept fresh by check-handbook

- **Source.** Ported from the field hub (knowledger-trans, commit c1d19c7), where a reader asking "which key does what, today?" had to read a scoping article whose current model sat below a superseded first table.
- **What.** `knowledge/handbook/` — one page per subject, current state only, plain prose for developers and non-developers. Every page lists the concept articles it synthesises in `sources:`; one home per fact holds. `check-handbook` (+ 8 tests) fails a page with no or dead sources and warns when a source's `updated:` is newer than the page's; `pre-commit-gate` runs it as a warning when the wrapper exists and prints "not set up" otherwise; `kb-status` prints a `handbook:` line; `build-index` indexes the directory.
- **Why warn, in the gate.** Staleness is caused by a commit to a source (unlike check-dates), but the page is often still right — a failing gate would teach `--no-verify`.
- **Docs.** `concepts/methodology/handbook-layer.md` (new), `tooling/maintenance-tools.md`, GLOSSARY, LIVING_DOCS_OVERVIEW, CHANGELOG.
