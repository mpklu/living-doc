# Curl-able installer

One-command adoption of the living-documentation methodology.

## Quick install (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/mpklu/living-doc/main/install/install.sh | bash
```

Run from the root of the project you want to adopt living-docs in. The script will:

1. Detect whether the project is **greenfield** (new, mostly empty) or **brownfield** (existing codebase) and ask you to confirm.
2. Detect your hook framework (`pre-commit` / `husky` / `lefthook`) if any, and whether you have a GitHub remote.
3. Offer two modes: recommended setup (one Y) or custom (per-group prompts).
4. Show a plan of every file it would write/skip/merge before doing anything.
5. Install the selected pieces, atomically per file.
6. Print a "next steps" summary, with a paste-able Claude prompt as the headline action.

It's **idempotent** — re-running on a populated repo is safe. Existing files are skipped with a clear notice, never silently clobbered.

## Cautious install

If you'd rather inspect before running:

```bash
curl -fsSL https://raw.githubusercontent.com/mpklu/living-doc/main/install/install.sh -o install.sh
less install.sh             # review
bash install.sh --dry-run   # see what it would do
bash install.sh             # run for real
```

## Flags

| Flag | What it does |
| --- | --- |
| `--ref <tag\|branch>` | Methodology version to fetch (default: `main`). Once tags exist, pin via `--ref v0.1`. |
| `--dry-run` | Print the plan but write nothing. |
| `--force` | Overwrite existing files. **Destructive — only when you mean it.** |
| `--help` | Print usage. |

## What gets installed

Manifest at [`install/manifest.txt`](manifest.txt). Groups:

| Group | Contents | When auto-included (recommended mode) |
| --- | --- | --- |
| `core` | `CLAUDE.md`, `knowledge/` skeleton, frontmatter schema | Always |
| `cli` | `scripts/drift-check`, `scripts/validate-articles`, supporting Python | Always |
| `hook-<framework>` | Pre-commit hook config matching the detected framework | Always (defaults to `pre-commit` if none detected) |
| `action` | `.github/workflows/living-docs-drift-check.yml` | Only if a GitHub remote / `.github/` is detected |
| `prompts` | `LIVING_DOCS_FIRST_PROMPT.md` at repo root — paste into Claude to bootstrap your first 3 articles | Always |

Custom mode lets you pick any subset.

## Detection rules

**Greenfield** if the repo has ≤2 commits AND ≤1 source file (across common extensions). Otherwise **brownfield**. If detection's wrong, the confirmation prompt lets you override.

**Hook framework** detected by config file presence (`.pre-commit-config.yaml`, `.husky/`, `lefthook.yml`). Falls back to `pre-commit`.

**GitHub remote** detected by `.github/` directory presence or `origin` URL containing `github.com`.

## What it does *not* do

- Doesn't run `pre-commit install` / `husky install` / `lefthook install` — adopters do that themselves so the script doesn't surprise-modify their hook setup.
- Doesn't auto-merge into existing `.pre-commit-config.yaml` / `lefthook.yml`. If those already exist, the script prints the snippet and asks the adopter to merge by hand.
- Doesn't create commits.
- Doesn't install Claude Code or any other tooling.
- Doesn't phone home.

## Pinning to a version

Once the repo tags releases (`v0.1`, etc.), pass `--ref v0.1` to lock to that methodology version:

```bash
curl -fsSL .../install.sh | bash -s -- --ref v0.1
```

Without a `--ref`, you get whatever's on `main`. That's fine for trying it out; pin once you want reproducibility.

## Bash compatibility

Targets bash ≥3.2 (the version macOS ships). No bash-4 features (`mapfile`, associative arrays). Should work on Linux, macOS, and WSL out of the box. Untested on native Windows — recommend WSL.

## Why a curl installer in addition to the Skill?

The Skill (`skills/living-docs/`) is the polished interactive surface for users with Claude Code installed. The curl installer is the 30-second on-ramp for everyone else: no Claude Code requirement, no clone, just one command. Both adopt the methodology; pick whichever fits the user's setup.
