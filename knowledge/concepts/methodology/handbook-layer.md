---
title: The handbook — a current-state layer for every reader, kept fresh by its sources
description: "Concept articles are the source of truth and the record at once, so a reader who wants only what is true now reads through history. An optional knowledge/handbook/ holds one page per subject, current state only, in plain prose; every page lists the concept articles it synthesises in sources:, and check-handbook warns when a source changes after the page"
type: concept
area: methodology
updated: 2026-11-09
status: thin
affects: ['actions/drift-check/check_handbook.py', 'scripts/check-handbook', 'actions/drift-check/build_index.py']
references:
  - concepts/methodology/two-readers-one-article.md
  - concepts/methodology/decisions-in-the-article.md
  - concepts/methodology/what-cache-why-asset.md
---

# The handbook — a current-state layer for every reader

## The problem

A concept article does two jobs. It is the **source of truth** — the place a claim lives — and it is the
**record**: dated evidence, provenance tags, decisions, corrections, "until 2026-09 this was…". The
record is what makes an article trustworthy and what an agent needs before changing code. It is also
what a reader who only wants *what is true now* has to read through.

That reader is common: a support engineer, QA, an administrator, a developer new to a subject. The
facts register (`facts/`) does not serve them — it is an agent's grep surface of identifiers. The
plain-terms rendering (`guide/`) does, partly: it is bullets per article, so a subject spread across
four articles is four fragments.

Observed in the field hub (2026-11-09): the article on API-key scoping held the current model only in
its later, dated sections, with a superseded model still in its first table — correct as a record,
confusing as an explanation.

## The layer

`knowledge/handbook/` beside `concepts/`, optional:

- **One page per subject**, named for what readers ask about ("Platform keys and scopes"), not for a
  code area. Plain prose first; identifiers in tables.
- **Current state only.** No dates as history, no "until…", no inline provenance tags.
- **A synthesis, never a source.** Every claim on a page also lives in a concept article. The page lists
  those articles in frontmatter `sources:` (paths under `knowledge/`) and points to them for the why.
  Articles in other repositories go in free-text `external_sources:`. *One home per fact* still holds:
  the handbook is a view, like `facts/` and `guide/`, except that a person writes it.
- Frontmatter: `updated`, `area: handbook`, `description`, `sources:`, optional `external_sources:`.
  No `affects:` — pages document subjects, not code paths, so the same-task rule reaches them through
  their sources.

## Keeping it fresh

A second layer goes stale silently: code changes touch the concept article, never the page. So the
coupling is made mechanical. `check-handbook`:

- **errors** on a page with no `sources:` (it cannot be checked and defers to nothing), and on a source
  that names no file;
- **warns** when a source's `updated:` is later than the page's own — the source changed since the page
  was last read against it. `--strict` turns this into an error.

The fix for a warning is a **re-read**, then bumping the page's `updated:` even if nothing on it
changed. Warn, not fail: the page is often still right, and a gate that fails on correct pages teaches
`--no-verify`. Unlike `check-dates`, it belongs in the commit gate, because a stale page is caused by a
commit (someone updated a source), not by the calendar. `kb-status` prints a `handbook:` line.

The same-task rule gains one sentence: when you change a concept article, find the handbook pages that
cite it (`grep -rl "<article path>" knowledge/handbook/`) and re-read them in the same task.

## What it does not catch

- **Wrongness at writing time.** The check knows a page is older than its sources, not that it was ever
  right. Writing a page is a synthesis and gets the same review as an article.
- **External sources.** `external_sources:` is free text the check cannot see; a page that leans mainly
  on another repository needs a periodic read.
- **`updated:` discipline.** The comparison trusts the field; an article edited without bumping
  `updated:` does not mark its pages stale. `bump-updated` and the gate's existing checks are the
  defence.

## Alternatives considered

- **Restructure concept articles to lead with current state.** Helps, but a subject still spans
  several articles, and the reorder fights the article's other job as a record.
- **A separate current-state knowledge base.** Two sources of truth; drift with no detector.
- **Grow `guide/`.** Generated bullets per article cannot carry a subject-level explanation.

## Adopting it

1. Add `handbook` to `ARTICLE_ROOTS` in `build_index.py` (this repo's engine already has it) and a
   `handbook` scope line to `scopes.md` once the first page exists.
2. Install `scripts/check-handbook`; the gate step runs it when present and prints "not set up"
   otherwise, so the gate is safe to share with KBs that have not adopted it.
3. Record the convention and the extended same-task sentence in `CLAUDE.md`.
4. Write the first page for the subject readers ask about most.

## Decisions

- 2026-11-09 — a separate `handbook/` of synthesised pages with checked `sources:`, over leading concept
  articles with current state or a second knowledge base, because readers want subject-level current
  state while articles must stay the record, and only a sources-and-dates coupling keeps a second layer
  from going stale silently *(decision: Kun, field hub)*
