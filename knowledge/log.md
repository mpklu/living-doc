# Compile log

Append-only narrative of changes to `knowledge/`. Newest at top.

## [2026-04-29] bundle E + A + B | procedural templates, schema, affects-globs in drift-check

First wave of the methodology bundle. Three pieces, one cohesive
commit:

**E — procedural compliance into the templates.**
`templates/brownfield/CLAUDE.md` and `templates/greenfield/CLAUDE.md`
now ship with the failure-mode framing, the 6-step "Before any
commit" checklist, and the red-flag phrases. New adopters inherit
the procedural reinforcements by default. Updated
`procedural-vs-principle.md` to mark this shipped.

**A — frontmatter schema.**
`schemas/article-frontmatter.schema.json` shipped (JSON Schema
2020-12). Required: `title`, `type`, `area`, `updated`, `status`.
Optional: `affects` (globs), `load_bearing` (bool), `references`
(list). Updated `frontmatter-as-source-of-truth.md` to reflect
shipped status.

**B — affects globs in drift-check.**
- Added `affects:` frontmatter to all five existing methodology
  articles (one of `dogfooding`, `frontmatter-as-source-of-truth`,
  `affects-globs`, `local-vs-pr-enforcement`,
  `procedural-vs-principle`).
- `drift_check.py` extended with `parse_frontmatter_affects` and
  `parse_articles_affects`. Hand-rolled YAML parser (no PyYAML dep
  to keep the Action runtime lean). Glob matcher upgraded with a
  custom `_glob_to_regex` that handles `**` recursion natively
  (previous fnmatch-only would have silently failed on nested files
  under `actions/drift-check/**`).
- `main()` now unions the frontmatter-derived mapping with the
  legacy CLAUDE.md table. Adopters can migrate incrementally.
- Smoke-tested against this repo's own `knowledge/`: 13 mapping rows
  derived from 5 articles' frontmatter; `**` matches nested files;
  exact-name matches still work.

Same-task new article: `concepts/tooling/drift-check.md` covers the
script's internals, the hand-parser limitations, the `**` matcher's
mapping table, and the dogfooding loop where the Action runs against
itself.

Articles updated, `index.md` updated with the new tooling row, this
log entry. No published prose touched.

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
