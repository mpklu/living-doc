## [2026-04-29] follow-up | article frontmatter validator + affects scope lesson

`scripts/validate-articles` ships, closing the "deferred" item in
`frontmatter-as-source-of-truth.md`. Implementation in
`actions/drift-check/validate_articles.py` (co-located with
drift_check.py since they share the zero-deps philosophy and a
parser family).

Validation against the JSON Schema:
- Required fields present and non-empty.
- `type` and `status` enums.
- `updated` matches `YYYY-MM-DD`.
- `affects` / `references` are list-of-strings.
- Each `references:` entry exists at the resolved path (catches
  rename/delete drift).

Skips `index.md` and `log.md` by name (index/log, not concept
articles).

Smoke-tested:
- 7 of this repo's articles: all valid (`✅` clean).
- Synthetic bad article with 4 violations: caught all 4, exit 1.

Same-task article: `concepts/tooling/validate-articles.md`
documents the parser, the cross-reference check, and the
"schema-as-contract" footgun (Python doesn't ship a JSON Schema
validator, so the script's enum constants are hand-mirrored from
the schema file — drift between them surfaces fast but isn't
mechanically prevented).

`frontmatter-as-source-of-truth.md` updated: the "deferred" section
is now "shipped". `index.md` adds the new tooling row.

**`affects:` scope lesson.** Mid-commit, drift-check flagged a
spurious same-task violation on `dogfooding.md` because that
article's `affects:` listed `knowledge/index.md` — and every article
addition touches the index. Narrowed dogfooding's scope to
`CLAUDE.md` + `README.md` (files whose change would actually
*contradict* dogfooding's content). General principle: `affects:`
globs should match files whose change would invalidate the article,
not files the article references in passing.
