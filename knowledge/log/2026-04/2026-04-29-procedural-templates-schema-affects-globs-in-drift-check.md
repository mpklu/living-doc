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
