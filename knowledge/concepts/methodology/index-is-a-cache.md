---
title: The index is a cache — generate it per directory, curate only scope lines
description: "A hand-curated index rots at a cache's rate (it dropped 5 of 131 articles unnoticed) and the human reader did not use it. Routing is one generated _index.md per content directory, recursive; the only curated input is one scope line per directory"
type: concept
area: methodology
updated: 2026-11-09
status: thin
affects: ['actions/drift-check/build_index.py']
load_bearing: true
references:
  - concepts/methodology/frontmatter-as-source-of-truth.md
---

# The index is a cache

## What the field repo found in one day

1. Ten of eleven index sections were hand-written tables. An audit found
   they had silently dropped **5 of 131 articles** *(field: 2026-09-21)*.
   An index is a cache of frontmatter; invalidated by hand, it rots at
   exactly a cache's rate. Every section became generated.
2. The one human reader said he did not read the page. Everything except
   the articles is agent-facing. The curated prose around the tables was
   ~15k tokens of distraction; each blurb already lived in an article. The
   page was deleted.
3. A single generated manifest (40 KB) charged ~10k tokens per routed
   question for all twelve areas to pick one, and would reach 90 KB at
   300 articles. It was split per area.
4. A per-area file flattened the tree: a third directory level became a
   `###` inside a growing file, and the `manifest/` directory mirrored the
   tree by hand.

## The rule that survived

Every directory that holds articles, directly or below, gets a generated
`_index.md`: a table of its subdirectories (scope line, article count,
facts and decisions coverage) and a row per article of its own (title,
status, updated, F, D, affects roots). Routing is a walk from
`knowledge/_index.md` down; each hop is 0.3–8 KB and sits next to what it
indexes. A new folder at any depth follows the same rule with no tool
change.

The **only curated input** is `scopes.md`: one line per content directory,
keyed by path. A content directory without a line fails the gate — the fix
is one line.

The indexed roots are `concepts/`, `connections/` and, where a KB adopts
it, `handbook/` (2026-11-09); the handbook's pages are indexed like
articles, with an empty affects column — they document subjects, not code
paths ([handbook-layer](handbook-layer.md)).

## Why `_index.md`, not `README.md`

An article named `README.md` already existed inside an article
directory. The underscore also sorts first in a listing.

## Anti-patterns

- Convert-on-touch for an index. The cost of converting all of it is an
  afternoon; the cost of not converting is silent omission.
- A description column. It was 30 % of the bytes and, once title and
  scope line were present, rarely decided anything.
