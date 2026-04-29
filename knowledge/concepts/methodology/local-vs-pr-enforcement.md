---
title: Local + PR-time enforcement — layered defense
type: concept
area: methodology
updated: 2026-04-29
status: thin
---

# Local + PR-time enforcement

The drift check fires at two points: locally, before the commit lands,
and at PR time, before the merge. Same logic, same article-mapping
source. Layered because each layer catches a different failure mode.

## Why two layers

**Local pre-commit catches "I forgot."** The contributor (human or
LLM) intended to update the article but didn't. A local hook fails
the commit, the contributor adds the article update, the commit
lands clean. Cheapest possible feedback loop.

**PR-time check catches "I bypassed the local hook."** Pre-commit
hooks can be skipped (`git commit --no-verify`), uninstalled, or
absent on contributors who didn't run the install step. The PR check
runs in CI without the contributor's involvement. Reviewer sees the
red mark; merge is blocked until resolved.

Both layers consume the same article-mapping source (`affects:`
frontmatter, or legacy CLAUDE.md table). Same logic, two firing
points. Drift in either layer means drift in both.

## What ships

Three deliverables, none currently in the repo:

1. **CLI mirror of the GH Action.** `python -m living_docs.drift_check`
   (or equivalent) — same Python, same `drift_check.py` logic, runs
   without GitHub. Reads `BASE_REF` (default `main`), diffs working
   tree against it, applies the same check.
2. **Pre-commit hook templates** under `templates/hooks/`:
   `pre-commit-config.yaml` (for the [pre-commit] framework),
   `husky.config.js`, `lefthook.yml`. Adopters drop in whichever
   matches their stack.
3. **Adoption-guide updates.** Both guides should say "wire in the
   local hook; the PR Action is the safety net." Today they only
   mention the Action.

[pre-commit]: https://pre-commit.com

## Why pre-commit, not pre-push

Pre-commit fails fast: contributor sees the failure before they've
moved on. Pre-push runs after the local commit is already authored;
the contributor has to amend, which is more friction. Cost of false
positives is also lower at commit time (you're already in the editor).

Pre-push is fine as a backup if the contributor's editor doesn't run
pre-commit hooks (e.g., GUI-only flows). Document but don't default.

## What each layer catches that the other doesn't

| Failure mode | Local hook | PR check |
| --- | --- | --- |
| Contributor forgot the article update | ✅ catches | ✅ catches |
| Contributor used `--no-verify` | ❌ misses | ✅ catches |
| Contributor doesn't have the hook installed | ❌ misses | ✅ catches |
| Article exists but is stale (content drift, not file drift) | ❌ misses | ❌ misses |
| Cross-link in article points to deleted article | ❌ (this check) | ❌ (this check) |

The last two require different tooling (drift sweep + reference
validator), tracked separately.

## Performance and noise

Local hooks must be fast (< 500ms) or contributors disable them. The
drift check should:

- Touch only `git diff --name-only`, not the working tree.
- Read frontmatter from articles (small, fast).
- Skip when CLAUDE.md is absent (early-stage adopter).

Noise reduction: the check should produce **zero output** on the
happy path. Speak only when there's something to fix.

## Files

- `actions/drift-check/drift_check.py` — current implementation
  (Action-only). Will be split into a library + thin Action wrapper
  + thin CLI wrapper.
- `templates/hooks/` — planned pre-commit templates
- `affects-globs.md` — the source the check consumes
- `procedural-vs-principle.md` — what the contributor follows when
  the check tells them they missed an article
