## [2026-04-29] readme refresh | surface shipped tooling for adopters

README was a fine landing page but trailed the actual surface:
no mention of `scripts/`, `schemas/`, `templates/hooks/`, the
`affects:` frontmatter shift, or `validate-articles`. A first-time
adopter reading only the README would get a worse adoption (PR-only
enforcement) than what's available.

Changes:
- "What's in this repo" table gains rows for `templates/hooks/`,
  `scripts/`, `schemas/article-frontmatter.schema.json`.
- New "What's enforced, and where" section between Pattern 3 and
  the Quick Starts. Three-row table covering agent rule (template
  CLAUDE.md), local hook (templates/hooks/ + scripts/drift-check),
  and the PR Action. Calls out `affects:` frontmatter as the
  canonical mapping source with a pointer to the schema and the
  validator.
- Pattern 2 (copy a template) gains an optional follow-up step
  for copying a hook template + scripts/.
- Roadmap line at the bottom updated: templates / Skill / Action /
  CLI / schema all marked shipped; remaining items called out.

Same-task article: `dogfooding.md` Files section adds a note about
README's enforcement-summary section, since dogfooding is what
stress-tests that layered enforcement on this repo. No other article
content changed — README expansion surfaces tooling that already
shipped, doesn't introduce new methodology decisions.
