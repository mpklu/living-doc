# Changelog

This file records changes to the methodology itself (the three core docs and supporting artifacts in this repo). Versions follow [SemVer](https://semver.org):

- **MAJOR** — breaking changes (rename of directories like `concepts/`, change in required `CLAUDE.md` structure). Adopters referencing the repo by URL should re-read the guides.
- **MINOR** — new optional patterns or supporting tooling. Backward-compatible.
- **PATCH** — clarifications, typo fixes, examples added.

If you reference this repo by URL in your project's `CLAUDE.md`, pin to a tag (e.g. `v0.1.0`) for reproducibility. Without a pin you get whatever's on `main`.

## [Unreleased]

_(no unreleased changes)_

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
