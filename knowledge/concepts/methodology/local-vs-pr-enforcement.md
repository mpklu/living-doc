---
title: Local + PR-time enforcement — layered defense
type: concept
area: methodology
updated: 2026-04-29
status: thin
affects:
  - 'actions/drift-check/**'
  - 'scripts/drift-check'
  - 'templates/hooks/**'
load_bearing: true
references:
  - concepts/methodology/affects-globs.md
  - concepts/methodology/procedural-vs-principle.md
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

## What ships (2026-04-29)

Three deliverables:

1. **CLI mirror of the GH Action** at `scripts/drift-check`. Wraps the
   same `drift_check.py` the Action uses. Argparse-driven, prints the
   report on stdout, exits 1 on violations (or 0 with `--warn-only`).
   Implementation detail: the wrapper walks up to find the repo root
   and `sys.path.insert`s the Action's directory, so it works without
   installing a package.
2. **Pre-commit hook templates** under `templates/hooks/`:
   - `pre-commit-config.yaml` (for the [pre-commit] framework)
   - `husky-pre-commit` (Husky shell hook)
   - `lefthook.yml` (Lefthook config)
   - `README.md` with installation notes for each, plus guidance on
     `--base-ref` choice (`HEAD` = staged-only for pre-commit,
     `HEAD~1` for post-commit, `origin/main` for branch-wide).
3. **Library split inside `drift_check.py`.** A new I/O-free `run_check()`
   takes paths + base ref, returns a result dict. Both `main()`
   (env-driven, GH Action) and `cli_main()` (argparse-driven) call
   into it. Same logic, two surfaces. See
   `concepts/tooling/drift-check.md`.

Adoption-guide updates remain pending; will land when the guides are
next touched (per "document on touch, not on inventory").

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

- `actions/drift-check/drift_check.py` — shared core (`run_check`)
  plus thin `main()` (Action) and `cli_main()` (CLI) wrappers. Library
  split shipped 2026-04-29.
- `scripts/drift-check` — local CLI shim that finds the repo root
  and dispatches to `cli_main()`.
- `templates/hooks/` — pre-commit, husky, and lefthook templates,
  all passing `--base-ref HEAD` (staged-only diff).
- `affects-globs.md` — the source the check consumes.
- `procedural-vs-principle.md` — what the contributor follows when
  the check tells them they missed an article.
