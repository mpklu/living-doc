---
title: Scripts over reasoning — mechanize the checkable
description: "Anything checkable by string/date/path comparison must be a script; AI reasoning is reserved for semantics. The boundary rule that keeps agent effort on judgment instead of bookkeeping"
type: concept
area: methodology
updated: 2026-07-22
status: thin
load_bearing: false
references:
  - concepts/tooling/maintenance-tools.md
  - concepts/methodology/local-vs-pr-enforcement.md
---

# Scripts over reasoning

**The rule: anything checkable by string, date, or path comparison must be
a script. AI reasoning is reserved for semantics.**

The methodology leans on an AI agent to enforce the same-task rule — but
"the agent enforces it" quietly became "the agent *re-derives* it, every
session": which index rows are stale, whether `updated:` got bumped,
whether that renamed file left dangling links, which articles are oldest
for the sweep. Each is a deterministic check. Spending model reasoning on
them is (a) expensive, (b) unreliable — an agent that forgets a mechanical
step under a big diff fails silently, exactly like the human it replaced.

## Field evidence (one production adoption, ~100 articles, ~3 months)

- Hand-synced index rows drifted repeatedly; after one sweep, 7 rows'
  dates/summaries were wrong until an agent hand-fixed them → `build-index`.
- Two companion files were deleted; references dangled until a manual
  grep found them → `check-links`.
- `updated:` bumps were forgotten or hand-edited ~10×/week → `bump-updated`.
- The monthly drift sweep began with the agent re-scanning all frontmatter
  to find the oldest articles → `sweep-report`.
- The active log outgrew its readable window in ~6 weeks; archiving by
  hand risked losing entries → `roll-log` (conservation-checked).

All five now exist: [[maintenance-tools]].

## The boundary

Script-side (deterministic): frontmatter validity, `affects:`-glob drift,
link resolution, index generation, date bumping, sweep ordering, log
rotation. Prospective candidates in the same class: stale-date flagging
(past dates near future-tense phrasing), `affects:`-glob liveness against
the source tree, secret/PHI pattern linting.

Reasoning-side (semantic): is this prose stale *in meaning*; does this
change alter documented behaviour; where does a new article belong; what's
the *why* worth capturing. This is where the agent's effort belongs — the
scripts exist to protect it.

Corollary for hook design: every script has a `--check`/exit-code mode so
it can gate commits and CI ([[local-vs-pr-enforcement]]), not just advise.
