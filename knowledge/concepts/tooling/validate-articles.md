---
title: validate-articles — internals
type: concept
area: tooling
updated: 2026-04-29
status: thin
affects:
  - 'actions/drift-check/validate_articles.py'
  - 'scripts/validate-articles'
  - 'schemas/article-frontmatter.schema.json'
load_bearing: true
references:
  - concepts/methodology/frontmatter-as-source-of-truth.md
  - concepts/tooling/drift-check.md
---

# validate-articles internals

Walks `knowledge/**/*.md` and verifies each article's frontmatter
against the shipped JSON Schema. Distinct from drift-check: drift-check
asks "did the contributor touch the right article when they changed
mapped code?"; validate-articles asks "is each article's metadata
well-formed and internally consistent?".

## Why a separate tool

Two different failure modes:

- drift-check fails when same-task discipline lapses. Article exists
  and is correct, but the contributor didn't touch it.
- validate-articles fails when an article is malformed: missing
  required field, wrong enum value, broken `references:` link.

Same-task discipline is enforced at PR time (Action) and
optionally at commit time (local hook). Frontmatter validity matters
the moment the article is *written* — wrong frontmatter goes
unnoticed by drift-check (it just reads `affects:` and moves on) but
silently weakens the entire mapping. Validating earlier closes that
gap.

## Hand-rolled YAML parser

`parse_frontmatter(article_path)` is a richer cousin of drift_check's
`parse_frontmatter_affects` — it returns the full frontmatter dict,
not just the `affects:` list. Same zero-deps philosophy: the schema
ships with the methodology, so the parser only has to handle exactly
the shapes the schema permits.

Supported:

- Scalar fields (`title:`, `type:`, etc.) — values can be unquoted,
  single-quoted, or double-quoted.
- Booleans (`load_bearing: true`).
- Block lists (`affects:` / `references:` followed by indented `-`
  items).
- Inline lists (`affects: [a, b, c]`).
- Comments and blank lines are ignored.

Not supported (intentionally — flag in PR review if needed):

- Nested objects.
- Anchors / aliases.
- Multi-document YAML (`---` separators inside frontmatter).

## What the validator checks

Per `schemas/article-frontmatter.schema.json`:

- Required fields (`title`, `type`, `area`, `updated`, `status`)
  present and non-empty strings.
- `type` ∈ `{concept, connection, meta}`.
- `status` ∈ `{thin, mature, deprecated}`.
- `updated` matches `^\d{4}-\d{2}-\d{2}$`.
- `load_bearing` is boolean if present.
- `affects` is a list of non-empty strings if present.
- `references` is a list of strings ending in `.md`, AND each
  referenced article exists at `knowledge_dir/<ref>`.

The cross-reference check is the only one that touches the
filesystem beyond the article being validated. It catches a
common drift mode: article A `references:` article B; B gets
renamed or deleted; A's frontmatter goes stale.

## Skipped files

`index.md` and `log.md` are skipped by name. They're index/log
artefacts, not concept articles, and don't have frontmatter (by
convention; nothing structural prevents it).

## Failure-mode shape

The CLI prints a per-file summary:

```text
⚠️ Frontmatter validation: 4 error(s) across 1 file(s) (checked 1).

  /path/to/bad-article.md:
    - type 'invalid_type' not in {concept, connection, meta}
    - updated 'not-a-date' must match YYYY-MM-DD
    - reference 'missing.md' not found at .../missing.md
    - reference 'no-extension' must end in .md
```

Exits 1 if any errors; 0 if clean. `--json` flag emits machine-
readable output for CI integration.

## Schema-as-contract caveat

The validator's enum lists and required-field tuple are
hand-mirrored from the JSON Schema (Python doesn't ship a JSON
Schema validator, and adding one is a dep we're avoiding). If the
schema changes, this module's constants must follow. There's no
automatic enforcement — the schema and validator stay in sync via
the same-task rule applied to themselves.

This is the kind of footgun that an integration test could close,
but the validator is small enough that drift here surfaces fast in
practice.

## Files

- `actions/drift-check/validate_articles.py` — implementation
- `scripts/validate-articles` — local CLI wrapper
- `schemas/article-frontmatter.schema.json` — the contract
- `concepts/methodology/frontmatter-as-source-of-truth.md` — design
  doc for the schema itself
