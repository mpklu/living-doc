# Changelog

This file records changes to the methodology itself (the three core docs and supporting artifacts in this repo). Versions follow [SemVer](https://semver.org):

- **MAJOR** — breaking changes (rename of directories like `concepts/`, change in required `CLAUDE.md` structure). Adopters referencing the repo by URL should re-read the guides.
- **MINOR** — new optional patterns or supporting tooling. Backward-compatible.
- **PATCH** — clarifications, typo fixes, examples added.

If you reference this repo by URL in your project's `CLAUDE.md`, pin to a tag (e.g. `v0.1.0`) for reproducibility. Without a pin you get whatever's on `main`.

## [Unreleased]

### Added — maintenance tooling (from field adoption of a ~100-article production knowledge hub)
- `scripts/check-links` (+ `actions/drift-check/check_links.py`) — verifies `[[wikilinks]]` and relative markdown links resolve; ambiguous wikilinks are errors; code fences/inline code excluded; repeatable `--exclude` glob for append-only surfaces like log archives (added during the first re-adoption run, which surfaced 49 real/legacy link problems in the field repo).
- `scripts/build-index` (+ `build_index.py`) — regenerates `index.md` article tables from frontmatter inside `<!-- build-index:begin dir=… -->` markers; `--check` mode for CI. This repo's own `knowledge/index.md` is now generated.
- `scripts/bump-updated` (+ `bump_updated.py`) — sets `updated:` to today on given/`--staged` articles; `--check` mode for pre-commit gating.
- `scripts/sweep-report` (+ `sweep_report.py`) — drift-sweep worklist: the N oldest articles by `updated:`.
- `scripts/roll-log` (+ `roll_log.py`) — rolls old log entries into monthly `knowledge/log/YYYY-MM.md` archives; conservation-checked (no entry can be silently lost); supports newest-first and oldest-first logs. Ported from the field adoption where it ran in production.
- Optional `description:` frontmatter field (schema + validator): one-line retrieval hook; fills the "Covers" column of generated index tables.
- `knowledge/concepts/tooling/maintenance-tools.md` and `knowledge/concepts/methodology/scripts-over-reasoning.md` — the tools' internals and the principle behind them.
- `templates/hooks/` — companion pre-commit hooks for `bump-updated --check`, `check-links`, `build-index --check`, and `build-facts --check`; plus the framework-free single-gate pattern (a versioned gate script exec'd from a plain `.git/hooks/pre-commit`, mirrored in CI as the `--no-verify` safety net).
- `scripts/check-affects` (+ `check_affects.py`) — `affects:` hygiene linter: free text and `knowledge/**`-tree claims are errors; dead globs / dead bare literals warn (glob-liveness vs the repo and repeatable `--source-root`); `external:`-prefixed cross-repo entries exempt. Generalizes the four latent mapping bugs the commit gate's maiden run caught in the field.
- `drift_check.py` — glob matcher expands bash-style brace alternation (`{a,b}`); field liveness sweep found brace-style affects entries that had silently never matched.
- `drift_check.py` — `affects:`-sourced rows are matched `force_glob` (the natural-language keyword fallback is now truly legacy-table-only; a bare affects filename once keyword-matched "data" against "datadog"), and `external:`-prefixed affects entries are skipped (cross-repo documentation convention, now blessed).
- **Facts register** (seeded as an optional pattern — the read path's "layer 1"): articles may carry a compact `## Facts` section of atomic, provenance-tagged lookup facts; `scripts/build-facts` (+ `build_facts.py`) concatenates them per `area:` into generated `knowledge/facts/<area>.md` surfaces (sentinel first line, orphan cleanup, `--check` gate) — a needle query loads one small file instead of 20–60KB of prose. Design: `knowledge/concepts/methodology/facts-register.md`. `sweep-report` now skips `log/` archives and generated `facts/` files (noise fix).
- **Claim provenance** (seeded as an optional pattern): inline tags grading how each load-bearing claim was verified — `*(code: path:line)*` · `*(bench: date)*` · `*(field: incident)*` · `*(reported: who)*` · `*(inferred)*` — so readers calibrate trust per claim. Design: `knowledge/concepts/methodology/claim-provenance.md`; tooling: `scripts/provenance-report` (+ `provenance_report.py`) — per-article tag coverage and `--worklist` (every inferred/reported claim in a `load_bearing` article = the generated verification worklist). Glossary entry + a pointer in `LIVING_DOCS_OVERVIEW.md` decision rule 4; guides/templates fold-in deferred until field-validated.

### Changed
- `knowledge/index.md` article tables are generated (`build-index`), with per-article summaries migrated verbatim into each article's `description:` frontmatter (single source).
- `ROADMAP.md` — new "Candidate refinements from field adoption (2026-07)" section.

## [0.1.0] — 2026-04-29

First tagged release. Pinable via `--ref v0.1.0` in the curl installer or any URL-reference adoption.

### Added — published methodology
- Three core documents:
  - `LIVING_DOCS_OVERVIEW.md` — meta-document with first principle and decision rules
  - `GREENFIELD_ADOPTION_GUIDE.md` — 8-step setup for new projects
  - `BROWNFIELD_ADOPTION_GUIDE.md` — 12-step retrofit for existing codebases (multi-repo workspace patterns included)
- `GLOSSARY.md` — methodology vocabulary
- `ROADMAP.md` — phased plan for next-phase work
- `CLAUDE.md` (in repo root) — methodology applied to this repo (dogfooded)

### Added — adoption surface
- `install/install.sh` + `install/manifest.txt` + `install/README.md` — curl-able one-command installer (Pattern 0). Bash 3.2+, manifest-driven, idempotent re-runs, `--dry-run` / `--force` / `--ref` flags. Detects greenfield vs. brownfield, hook framework, GitHub remote.
- `templates/greenfield/`, `templates/brownfield/`, `templates/workspace-level/` — copy-paste starters for `CLAUDE.md` + `knowledge/` skeleton.
- `templates/hooks/` — pre-commit hook configs for the pre-commit framework, husky, and lefthook (local enforcement at commit time).
- `templates/prompts/` — paste-able Claude prompts (`first-articles-greenfield.md`, `first-articles-brownfield.md`) for bootstrapping the first three thin articles after adoption.
- `templates/pr-template-snippet.md` — drop-in PR template snippet.
- `skills/living-docs/` — Claude Code Skill scaffolding for interactive adoption.

### Added — tooling
- `actions/drift-check/` — GitHub Action verifying same-task-rule compliance on PRs. Library-split internals (I/O-free `run_check()` core + thin `main()` and `cli_main()` wrappers).
- `actions/drift-check/validate_articles.py` — frontmatter schema validator with cross-reference check.
- `scripts/drift-check`, `scripts/validate-articles` — local CLI shims, zero-deps Python, run from any directory inside the repo.
- `schemas/article-frontmatter.schema.json` — JSON Schema contract for article frontmatter (`title`, `type`, `area`, `updated`, `status`, optional `affects:` globs, `references`, `load_bearing`).

### Added — meta-repo dogfooding
- `knowledge/` — methodology applies to itself; concept articles under `knowledge/concepts/{methodology,tooling}/` capture the *why* behind decisions in this repo.

### Notes
- The `**` glob matcher in `drift_check.py` correctly handles recursion (Python's stdlib `fnmatch` collapses `**` to `*`); a custom translator was needed.
- The local pre-commit hook uses `git diff --cached` (staged-only) — unstaged dirty files are intentionally excluded to avoid false positives against articles whose `affects:` happens to match dirty paths.

## How to read past entries

Each tagged release appears as its own section here with the date and a summary of changes. Entries follow [Keep a Changelog](https://keepachangelog.com/) loosely — Added / Changed / Deprecated / Removed / Fixed / Security as needed.
