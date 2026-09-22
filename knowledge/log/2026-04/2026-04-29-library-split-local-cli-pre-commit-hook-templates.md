## [2026-04-29] bundle C | library split + local CLI + pre-commit hook templates

The remaining bundle piece. drift_check.py refactored so the same
core logic (`run_check`) is reachable from both the GH Action's
env-driven `main()` and a new argparse-driven `cli_main()`. The
script's `__main__` block dispatches based on `GITHUB_ACTIONS` env.

`scripts/drift-check` shipped as the local CLI shim — walks up to
the repo root, adds `actions/drift-check/` to `sys.path`, calls
`cli_main()`. Works from any directory, no package install needed.

Pre-commit hook templates under `templates/hooks/`:
- `pre-commit-config.yaml` for the pre-commit framework
- `husky-pre-commit` for Husky
- `lefthook.yml` for Lefthook
- `README.md` with installation notes for each + guidance on
  `--base-ref` choice (HEAD for pre-commit, origin/main for CI)

`get_changed_files` got a small but load-bearing fix: when
`base_ref == "HEAD"`, use `git diff --name-only HEAD` (working tree
vs HEAD) instead of `HEAD...HEAD` (empty). Pre-commit usage now
correctly inspects the about-to-be-committed state.

**Self-dogfooding moment.** First local run flagged a same-task
violation: I'd modified drift_check.py without touching
`affects-globs.md` (which `affects:` it). Updated the article with a
one-line note about the library split, re-ran, passed. The mechanism
catching itself was the most credible validation of the approach.

Articles updated:
- `concepts/tooling/drift-check.md` — added "Library split" section,
  expanded `affects:` to include `scripts/drift-check` and
  `templates/hooks/**`.
- `concepts/methodology/local-vs-pr-enforcement.md` — replaced
  "What ships (planned)" with "What ships (2026-04-29)"; lists the
  three deliverables that landed.
- `concepts/methodology/affects-globs.md` — one-line note on the
  library split (the same-task touch that got me unstuck).

Bundle complete. A + B + C + E all shipped.
