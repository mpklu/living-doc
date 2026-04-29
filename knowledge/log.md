# Compile log

Append-only narrative of changes to `knowledge/`. Newest at top.

## [2026-04-29] retrofit | knowledge base established + first 5 articles

This repo now dogfoods the methodology it defines. Brownfield retrofit
started today, triggered by an active development seam: the next-phase
methodology bundle (frontmatter schema + `affects:` globs + local
enforcement + procedural compliance).

Skeleton:

- `CLAUDE.md` at repo root — slim spine + same-task rule + procedural
  pre-commit checklist + red-flag phrases. Adopts the recommendations
  from `concepts/methodology/procedural-vs-principle.md` from day one.
- `knowledge/index.md`, `knowledge/log.md`.
- `concepts/methodology/`, `concepts/tooling/`, `connections/`.

First five articles, all under `concepts/methodology/`:

- `dogfooding.md` — why this repo applies its own methodology; what
  makes meta-repos different (articles document maintainer decisions,
  not adopter-facing examples).
- `frontmatter-as-source-of-truth.md` — proposed frontmatter schema
  with required + optional fields; rationale for moving article
  metadata from CLAUDE.md tables into the articles themselves.
- `affects-globs.md` — `affects: [globs]` in frontmatter as the
  canonical code↔article mapping; auto-generated table; backward-
  compatible upgrade path for the GH Action.
- `local-vs-pr-enforcement.md` — local CLI mirror of the drift check
  + pre-commit hook templates; failure modes each layer catches.
- `procedural-vs-principle.md` — same-task rule recast as a 6-step
  checklist; red-flag phrases as STOP signals; failure-mode framing.

These five capture the design decisions for the upcoming bundle. The
bundle implementation will land as separate commits, each touching the
relevant article(s) per the same-task rule.

Existing prose (`LIVING_DOCS_OVERVIEW.md`, the two adoption guides,
`GLOSSARY.md`, the templates, the Skill, the GH Action) is left
untouched per "document on touch, not on inventory." Each will get
articles when next modified.
