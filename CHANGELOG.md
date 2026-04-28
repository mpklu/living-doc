# Changelog

This file records changes to the methodology itself (the three core docs and supporting artifacts in this repo). Versions follow [SemVer](https://semver.org):

- **MAJOR** — breaking changes (rename of directories like `concepts/`, change in required `CLAUDE.md` structure). Adopters referencing the repo by URL should re-read the guides.
- **MINOR** — new optional patterns or supporting tooling. Backward-compatible.
- **PATCH** — clarifications, typo fixes, examples added.

If you reference this repo by URL in your project's `CLAUDE.md`, consider pinning to a tag once tags exist.

## [Unreleased]

### Added
- Initial publication of the three core documents:
  - `LIVING_DOCS_OVERVIEW.md` — meta-document with first principle and decision rules
  - `GREENFIELD_ADOPTION_GUIDE.md` — 8-step setup for new projects
  - `BROWNFIELD_ADOPTION_GUIDE.md` — 12-step retrofit for existing codebases (includes multi-repo workspace patterns)
- `GLOSSARY.md` — methodology vocabulary
- `templates/` — copy-paste-ready starters for greenfield, brownfield, and workspace-level
- `skills/living-docs/` — Claude Code Skill scaffolding for interactive adoption
- `actions/drift-check/` — GitHub Action for verifying same-task-rule compliance on PRs
- `ROADMAP.md` — phased plan for next-phase work

## How to read past entries

Once the methodology has tagged versions, each release will appear as its own section here with the date and a summary of changes.
