---
title: install.sh — curl-able adoption installer
type: concept
area: tooling
updated: 2026-04-29
status: thin
affects:
  - 'install/**'
load_bearing: true
references:
  - concepts/methodology/prompts.md
  - concepts/methodology/local-vs-pr-enforcement.md
---

# install.sh internals

`install/install.sh` is the curl-able adoption on-ramp. One command lands the methodology in a target repo: detection → mode pick → plan view → atomic install → next-steps summary.

## Why bash, not Python or Node

Adopters run this *before* committing to the methodology. They shouldn't need to install a runtime first. Bash 3.2+ ships everywhere we care about (macOS default, every Linux, WSL). Trade-off: no associative arrays, no `mapfile`. We use parallel indexed arrays (`MANIFEST_GROUPS`, `MANIFEST_SRCS`, `MANIFEST_DESTS`, `MANIFEST_MODES`) instead of one assoc.

## Manifest as the contract

`install/manifest.txt` is a flat text file mapping `group:source_in_repo -> dest_in_target_repo (mode)`. The script fetches the manifest first (pinned to `--ref`), then iterates. New groups or new files don't require script changes — only manifest changes. The format is simple enough to parse with parameter expansion (`${rest%% -> *}`); no jq/yq dep.

Modes: `add-only` (skip if dest exists), `merge` (print snippet for manual merge if dest exists), `exec` (chmod +x after writing). Modes combine: `add-only,exec`.

## Detection bias

Greenfield only when the signals are clear (≤2 commits AND ≤1 source file across common extensions). Bias toward brownfield when ambiguous — a false brownfield call is harmless (more careful prompts), a false greenfield call could produce inappropriate articles. The user confirms regardless.

## Atomic per-file write

Each file is fetched to `${TMP_DIR}/staged-N`, then `mv`'d into place. A Ctrl+C mid-install leaves either a complete file or no file — never half a file. Cross-file atomicity isn't attempted; each file's individual atomicity is sufficient.

## Re-runs are safe

Existing files are skipped by default with a clear notice. `--force` opts into overwriting. `--dry-run` prints the plan and writes nothing — useful for review before committing to the change.

## What it deliberately doesn't do

- Run `pre-commit install` / `husky install` / `lefthook install`. Adopter hook setup is theirs to manage.
- Auto-merge into existing hook configs. We print the snippet; they merge.
- Create commits. The summary prints a suggested commit; the adopter runs it.
- Phone home, install Claude Code, or modify shell rc files.

## Files

- `install/install.sh` — the script
- `install/manifest.txt` — the file-list contract
- `install/README.md` — adopter-facing usage
