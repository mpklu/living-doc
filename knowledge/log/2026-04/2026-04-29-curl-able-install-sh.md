## [2026-04-29] new surface | curl-able install.sh

`install/install.sh` shipped — the one-command adoption on-ramp.
`curl ... | bash` from a project root, the script detects
greenfield vs brownfield, asks to confirm, offers recommended-mode
or custom-mode install, prints a plan, then atomically lands the
right mix of `CLAUDE.md` / `knowledge/` / `scripts/` / hook config /
GitHub Action / paste-able Claude prompt.

Design choices captured in `concepts/tooling/install-script.md`:

- **Bash 3.2+, no other runtime.** Adopters run this *before*
  committing to the methodology — they shouldn't need to install
  anything first. macOS default bash dictates the floor.
- **Manifest-driven.** `install/manifest.txt` is a flat
  `group:src -> dest (mode)` text file. New files don't require
  script changes — only manifest edits. Modes: `add-only`, `merge`
  (snippet print for adopters with existing configs),
  `add-only,exec` (chmod +x).
- **Detection biased toward brownfield.** Greenfield only when ≤2
  commits AND ≤1 source file. Ambiguous → brownfield (safer; false
  brownfield is harmless, false greenfield could produce bad
  articles).
- **Atomic per-file write.** Fetch to `${TMP_DIR}/staged-N`,
  `mv` into place. Per-file atomicity is sufficient; cross-file
  transactional install isn't attempted.
- **Idempotent.** Existing files skipped by default with a clear
  notice. `--force` to overwrite; `--dry-run` to preview.
- **Doesn't:** auto-run `pre-commit install` / `husky install` /
  `lefthook install`; auto-merge into existing hook configs;
  create commits; install Claude Code; modify shell rc files.

Smoke-tested in `/tmp` sandboxes:
- Greenfield (1 commit, no source files) → detected greenfield,
  installed `core+cli+hook-pre-commit+prompts`, 12 files written
  atomically.
- Re-run on the populated sandbox → all `add-only` files skipped
  with clear notice; `merge`-mode `.pre-commit-config.yaml`
  printed snippet for manual merge. Idempotent confirmed.

Bug found and fixed in pre-commit testing: the summary heredoc
contained an inline `${[[...]] && printf || printf}` substitution,
which bash doesn't support inside heredoc `${...}`. Replaced with
a `local` variable computed before the heredoc. The kind of bug
that only shows up at the end of a run, after the install was
otherwise successful — caught here, before adopters hit it.

Same-task collateral:
- New article `concepts/tooling/install-script.md` covers
  `install/**`. Captures the bash-not-Python decision, the
  manifest-as-contract pattern, atomic per-file write, and the
  deliberate non-actions.
- README "How to use this repo" gains a new **Pattern 0** at the
  top: the curl one-liner, with a one-paragraph explanation. The
  three existing patterns get renumbered conceptually but keep
  their content.
- README "What's in this repo" gains a row for `install/`.
- `index.md` adds the install-script row.
