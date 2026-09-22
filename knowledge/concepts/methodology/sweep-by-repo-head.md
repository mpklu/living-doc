---
title: Sweep by repo HEAD before reading prose
description: "A stale article whose repo has had no commits since it was written cannot have drifted from code. Check git log first; read the article only when the repo moved. Five of six stale articles were verified in one line each"
type: concept
area: methodology
updated: 2026-09-21
status: thin
affects: ['actions/drift-check/sweep_report.py']
load_bearing: false
references:
  - concepts/methodology/scripts-over-reasoning.md
---

# Sweep by repo HEAD before reading prose

## The observation

The drift sweep as written — "scan recently changed files against their
articles" — assumes the article is the expensive thing to read. On the
first real sweep of the field repo, the eight oldest articles were
untouched since April. For six of them, one command settled the question:

```bash
git -C <repo> log --since=<article updated:> --oneline | wc -l
```

Five repos returned **zero** *(bench: 2026-09-21)*. An article cannot
have drifted from code that has not changed. Each got a dated sweep note
under its H1 with the HEAD sha, and its `updated:` bumped — the field
means "last verified", not "last edited". The sixth repo was not checked
out locally: noted, not bumped.

## The rule

1. Oldest `updated:` first (`sweep-report`).
2. For each: repo HEAD date and commit count since `updated:`. Zero →
   verified; note and bump. Non-zero → list the commits that touch paths
   in `affects:`; read the article only against those.
3. Then `check-dates`: re-tense what is clearly past without inventing
   the outcome ("was expected …; not re-verified at the <date> sweep").
4. Log the sweep as one entry; leave what needs an outside source as an
   open, dated item.

## Why it matters

Reading a 5k-word article to confirm nothing changed is the expensive way
to learn what `git log` says in one line. The sweep's scarce resource is
attention; spend it on the repos that moved.

## Prerequisite

The sweep needs a trigger. "Once a sprint" in prose fired zero times in
four months; a session-start status line that prints the three stalest
articles fires every session ([[token-budget-per-surface]]).
