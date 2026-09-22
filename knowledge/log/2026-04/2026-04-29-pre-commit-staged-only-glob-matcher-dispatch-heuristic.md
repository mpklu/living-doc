## [2026-04-29] review pass | pre-commit staged-only, glob matcher, dispatch heuristic

Cross-session review of bundle C found three issues. All fixed in
this commit.

**1. Pre-commit hooks would fire on unstaged dirty files.**
`get_changed_files` with `base_ref == "HEAD"` ran `git diff HEAD`,
which is staged + unstaged. Pre-commit only commits staged files —
so any dirty-but-unstaged path with an `affects:` glob match would
trigger a same-task violation against an article the contributor
wasn't actually touching. Switched to `git diff --cached`. Hook
templates already pass `--base-ref HEAD`, so no template change
needed; `templates/hooks/README.md` updated to spell out
"staged-only" so the next adopter doesn't relearn the trap.

**2. `_glob_to_regex` `regex.rstrip(".*")` was structurally fragile.**
On a `**/` segment, the rstrip was supposed to remove the just-
appended `.*` before substituting `(?:.*/)?`. But `rstrip` strips
chars from a *set*, so it would happily eat trailing `.` and `*`
from prior tokens — corrupting patterns like `foo*/**/bar` (the
`*` from `[^/]*` would be stripped) or `.**/x` (the literal `\.`
would be stripped). Reworked to treat `**/` as a single token via
lookahead. No live article hit the bug, but the next adopter who
writes a complex glob would have hit it silently.

**3. Local CLI dispatch could mis-fire as Action mode.**
`__main__` treated either `GITHUB_ACTIONS=true` or `GITHUB_OUTPUT`
being set as Action mode. A developer with `GITHUB_OUTPUT` exported
in their shell from a prior CI debug session would silently route
`scripts/drift-check` to the env-driven `main()`. Tightened to
`GITHUB_ACTIONS=true` only.

Same-task article updates: `concepts/tooling/drift-check.md` gains
sections on `get_changed_files` resolution and the `**/`-as-single-
token rationale; the dispatch description drops the
`GITHUB_OUTPUT` clause and notes why. `concepts/methodology/local-
vs-pr-enforcement.md` Files section refreshed (was forward-looking,
now reflects shipped state) and the `--base-ref` line annotates
`HEAD` as "staged-only".

**Methodology observation.** All three bugs survived the original
bundle-C review — they were correctness issues hidden behind
plausible-looking code (`git diff HEAD` *seems* right; `rstrip`
*seems* like a clean post-process; `GITHUB_OUTPUT` *seems* like a
reasonable signal). The cross-session review caught them because
the second reader wasn't anchored to the first author's mental
model. Suggests a small principle worth capturing: cross-session
review is part of the methodology's value, not a bonus. Will fold
into a `procedural-vs-principle.md` revision when that article is
next touched, rather than write it now (capture-first, but in the
right place).
