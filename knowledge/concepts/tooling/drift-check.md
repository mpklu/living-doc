---
title: drift-check — internals
type: concept
area: tooling
updated: 2026-04-29
status: thin
affects:
  - 'actions/drift-check/drift_check.py'
  - 'actions/drift-check/action.yml'
  - 'scripts/drift-check'
  - 'templates/hooks/**'
load_bearing: true
references:
  - concepts/methodology/affects-globs.md
  - concepts/methodology/local-vs-pr-enforcement.md
---

# drift-check internals

`actions/drift-check/drift_check.py` is a small Python module run by
the GitHub Action of the same name. It validates the same-task rule
at PR-review time. This article captures how it works internally —
the design decisions, edge cases, and what would surprise a future
contributor reading the source.

## Library split — three entry points, one core

`run_check(claude_md_path, knowledge_dir, base_ref)` is the I/O-free
core. It returns a dict with `status`, `report`, `violations`,
`mapping_count`. Two thin wrappers consume it:

- **`main()`** — GitHub Action entry. Reads env vars
  (`CLAUDE_MD_PATH`, `KNOWLEDGE_DIR`, `BASE_REF`, `FAIL_ON_VIOLATION`),
  emits `violations` + `report` to `$GITHUB_OUTPUT`, prints the
  report, exits 1 on violations when `FAIL_ON_VIOLATION=true`.
- **`cli_main(argv)`** — local CLI entry. Parses args via argparse
  (`--claude-md`, `--knowledge-dir`, `--base-ref`, `--warn-only`),
  prints the report, exits 1 on violations unless `--warn-only`.

The `__main__` block dispatches: `GITHUB_ACTIONS=true` (or
`GITHUB_OUTPUT` set) → `main()`; otherwise → `cli_main()`. Both
behaviours from one file means both surfaces stay in sync as the
core evolves.

The repo's `scripts/drift-check` is a thin Python wrapper that walks
up to the repo root, adds `actions/drift-check/` to `sys.path`, and
calls `cli_main()`. Lets adopters invoke the check from any
directory in their repo without installing a package.

## Two mapping sources, merged

`run_check` builds the article-mapping by union:

1. **`parse_articles_affects(knowledge_dir)`** — walks
   `knowledge/**/*.md`, reads each article's YAML frontmatter, extracts
   the `affects:` list, emits one `MappingRow` per glob. This is the
   canonical source.
2. **`parse_article_mapping(claude_md_text)`** — parses the legacy
   markdown table in CLAUDE.md. Kept for backward compat; adopters
   migrate incrementally to `affects:` per the methodology.

The two are concatenated; downstream `check_drift` doesn't know or
care which source any given row came from.

## Hand-rolled YAML frontmatter parser

`parse_frontmatter_affects(article_path)` does not import PyYAML.
Reasons:

- The Action runs in a stock GitHub-hosted runner; adding deps means
  managing a `requirements.txt` plus a setup step in `action.yml`.
  Bandwidth not worth it for a 30-line parser.
- The frontmatter shape is documented in
  `schemas/article-frontmatter.schema.json` and stays simple. Block-
  list `affects:` (with `-` items, single- or double-quoted or
  unquoted) plus an inline `affects: [a, b]` shorthand cover every
  case we need.
- A lightweight parser doesn't have to handle YAML's full feature set
  (anchors, multi-document, complex types) because none of those
  appear in well-formed living-doc frontmatter.

Limitation worth knowing: malformed YAML in frontmatter (unbalanced
quotes, mis-indented list items) silently parses as "no affects."
Tradeoff: better than crashing the Action; revealed by the article
not appearing in drift-check output. Future improvement: a separate
`validate-articles` step that catches frontmatter issues at write
time.

## Glob matcher supports `**`

`_glob_to_regex(pattern)` is a custom translator because Python's
stdlib `fnmatch.fnmatch` collapses `**` to `*`. The translator
maps:

- `**` → `.*` (matches across path separators, including none)
- `**/` → `(?:.*/)?` (so `a/**/b` matches `a/b` AND `a/x/y/b`)
- `*` → `[^/]*` (single-segment match)
- `?` → `[^/]`
- regex meta-characters escaped

This matters because `affects:` patterns in articles routinely use
`**` (e.g., `'actions/drift-check/**'`). The previous fnmatch-only
behaviour would have silently failed to match nested files.

## Free-text fallback (legacy table only)

When a CLAUDE.md table row uses a natural-language description
("the LLM agent code"), `code_pattern_matches_files` falls back to
keyword matching: extracts non-trivial words and tests each changed
file's path. Imprecise; we keep it only because some early adopter
projects have such rows. New mappings (especially from `affects:`
frontmatter) should always use globs.

## Output contract

The Action emits two outputs to `$GITHUB_OUTPUT`:

- `violations` — count, as a string.
- `report` — markdown-formatted, ready to drop into a PR comment.

When `FAIL_ON_VIOLATION=false`, the Action exits 0 even with
violations (warn-only mode). Useful for adopters wanting to see what
the check would flag before turning it strict.

## Tested edge cases

The Action runs against itself (this repo dogfoods). Confirmed:

- Article with no `affects:` produces 0 rows (no false positives).
- Article with empty frontmatter (no `---` block) is skipped.
- Glob `actions/drift-check/**` matches `actions/drift-check/foo.py`
  AND `actions/drift-check/sub/bar.py`.
- Exact-filename pattern `CLAUDE.md` matches only `CLAUDE.md`.
- A changed article under `knowledge/` whose own `affects:` matches
  *itself* should not violate (article-changes-self is the desired
  case). Currently handled because the article is in `changed_set`
  and the check returns the matched path → article identity. Worth
  watching: edge cases in cross-article references.

## Future work tracked elsewhere

- Local CLI mirror — see `local-vs-pr-enforcement.md`.
- Article frontmatter validator — see
  `frontmatter-as-source-of-truth.md`.
- Drift sweep on `mature` articles — separate from this checker;
  documented when the sweep tooling lands.

## Files

- `actions/drift-check/drift_check.py` — the implementation
- `actions/drift-check/action.yml` — Action manifest
- `actions/drift-check/example-usage.yml` — reference workflow
- `schemas/article-frontmatter.schema.json` — input contract for
  the frontmatter parser
