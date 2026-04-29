# Compile log

Append-only narrative of changes to `knowledge/`. Newest at top.

## [2026-04-29] release | v0.1.0 cut

First tagged release. CHANGELOG.md rolled from `[Unreleased]` →
`[0.1.0] — 2026-04-29` with full inventory of what shipped:
methodology surface (3 core docs + glossary + roadmap),
adoption surface (install.sh + templates + prompts + Skill),
tooling (drift-check Action + library split + CLI shims +
validate-articles + frontmatter schema), meta-repo dogfooding
(`knowledge/`).

`install/README.md` references normalized from `v0.1` → `v0.1.0`
to match the actual tag name (SemVer 3-part). `install-script.md`
gains a "Version pinning" section explaining `--ref v0.1.0` and
why pinning matters (without a pin, today's install differs from
yesterday's because main moves).

CHANGELOG note worth preserving in log: the entries call out two
non-obvious correctness facts adopters might wonder about — the
custom `**` glob translator (because Python's fnmatch collapses
`**` to `*`) and the staged-only diff in pre-commit hooks (because
`git diff HEAD` includes unstaged dirty files, producing false
positives). Both were caught in the cross-session review pass that
preceded this tag.

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

## [2026-04-29] new surface | paste-able prompts under templates/prompts/

Two prompt files shipped under `templates/prompts/`:
`first-articles-brownfield.md` and `first-articles-greenfield.md`.
Each is a self-contained instruction block an adopter pastes into
Claude after running install (or any time they want to seed their
first three articles). The prompts encode the methodology
constraints — schema reference, same-task rule, "thin is fine,"
no speculative `affects:`, no back-fill past three — so a fresh
Claude session with no project context produces methodology-
compliant articles instead of generic "let me document this codebase
for you" output.

Decision: **prompts ship as markdown files in the repo, not as
shell-string-literals inside a future install.sh.** Reasons in
`concepts/methodology/prompts.md` (new): they're load-bearing
methodology surface, they version with reviewable diffs, schema
changes affect them, and they're discoverable for adopters who
return later.

Greenfield vs. brownfield split:
- Brownfield prompt scans the codebase: hot-spot modules, decision-
  dense areas, onboarding pain points. Caps at 3, no back-fill.
- Greenfield prompt asks 3–5 anchor questions first, then writes
  three "north star" articles with empty `affects:` (filled when
  the matching code lands).

Same-task collateral:
- New article `concepts/methodology/prompts.md` covers `templates/
  prompts/**`. Captures the load-bearing argument and the "what
  makes a good prompt" criteria (self-contained, constraint-stating,
  one screen, output-shaped).
- README "What's in this repo" gains a row for `templates/prompts/`.
- `templates/prompts/README.md` is the adopter-facing index for the
  directory.
- `index.md` adds the prompts article row.

The install.sh design (in conversation; not yet written) will copy
the appropriate prompt file based on greenfield/brownfield
detection and reference it in the post-install summary so adopters
can paste it into Claude as the first post-install action.

## [2026-04-29] design seed | session-handoff skill

Captured the design for a planned `skills/session-handoff/` skill in
`concepts/methodology/session-handoff.md`. Triggered by an
end-of-long-session observation: the methodology answers "how does
the next session know what's true" but doesn't yet answer the
corollary "how does the current session, before ending, capture
what won't otherwise survive context loss?" Article scopes the
skill's five phases (audit activity → audit durable capture →
identify gaps → generate handoff brief → surface next-session
opener) and the anti-patterns to design around (don't generate a
giant doc; don't replace the same-task rule).

Implementation deferred — picked up in a future session by whoever
needs it. The article's `affects:` declares `skills/session-handoff/**`
so when the implementation starts, the same-task rule guides
whoever's writing it back to this design doc.

Companion artifact: a one-time handoff doc landed in the mira repo
at `docs/reports/2026-04-29-mp-catalog-session-handoff.md` —
captures cursor / open items / next-session opener for the long
session this design article emerged from. That artifact is
ephemeral; this article is durable.

## [2026-04-29] readme refresh | surface shipped tooling for adopters

README was a fine landing page but trailed the actual surface:
no mention of `scripts/`, `schemas/`, `templates/hooks/`, the
`affects:` frontmatter shift, or `validate-articles`. A first-time
adopter reading only the README would get a worse adoption (PR-only
enforcement) than what's available.

Changes:
- "What's in this repo" table gains rows for `templates/hooks/`,
  `scripts/`, `schemas/article-frontmatter.schema.json`.
- New "What's enforced, and where" section between Pattern 3 and
  the Quick Starts. Three-row table covering agent rule (template
  CLAUDE.md), local hook (templates/hooks/ + scripts/drift-check),
  and the PR Action. Calls out `affects:` frontmatter as the
  canonical mapping source with a pointer to the schema and the
  validator.
- Pattern 2 (copy a template) gains an optional follow-up step
  for copying a hook template + scripts/.
- Roadmap line at the bottom updated: templates / Skill / Action /
  CLI / schema all marked shipped; remaining items called out.

Same-task article: `dogfooding.md` Files section adds a note about
README's enforcement-summary section, since dogfooding is what
stress-tests that layered enforcement on this repo. No other article
content changed — README expansion surfaces tooling that already
shipped, doesn't introduce new methodology decisions.

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

## [2026-04-29] follow-up | article frontmatter validator + affects scope lesson

`scripts/validate-articles` ships, closing the "deferred" item in
`frontmatter-as-source-of-truth.md`. Implementation in
`actions/drift-check/validate_articles.py` (co-located with
drift_check.py since they share the zero-deps philosophy and a
parser family).

Validation against the JSON Schema:
- Required fields present and non-empty.
- `type` and `status` enums.
- `updated` matches `YYYY-MM-DD`.
- `affects` / `references` are list-of-strings.
- Each `references:` entry exists at the resolved path (catches
  rename/delete drift).

Skips `index.md` and `log.md` by name (index/log, not concept
articles).

Smoke-tested:
- 7 of this repo's articles: all valid (`✅` clean).
- Synthetic bad article with 4 violations: caught all 4, exit 1.

Same-task article: `concepts/tooling/validate-articles.md`
documents the parser, the cross-reference check, and the
"schema-as-contract" footgun (Python doesn't ship a JSON Schema
validator, so the script's enum constants are hand-mirrored from
the schema file — drift between them surfaces fast but isn't
mechanically prevented).

`frontmatter-as-source-of-truth.md` updated: the "deferred" section
is now "shipped". `index.md` adds the new tooling row.

**`affects:` scope lesson.** Mid-commit, drift-check flagged a
spurious same-task violation on `dogfooding.md` because that
article's `affects:` listed `knowledge/index.md` — and every article
addition touches the index. Narrowed dogfooding's scope to
`CLAUDE.md` + `README.md` (files whose change would actually
*contradict* dogfooding's content). General principle: `affects:`
globs should match files whose change would invalidate the article,
not files the article references in passing.

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

## [2026-04-29] bundle E + A + B | procedural templates, schema, affects-globs in drift-check

First wave of the methodology bundle. Three pieces, one cohesive
commit:

**E — procedural compliance into the templates.**
`templates/brownfield/CLAUDE.md` and `templates/greenfield/CLAUDE.md`
now ship with the failure-mode framing, the 6-step "Before any
commit" checklist, and the red-flag phrases. New adopters inherit
the procedural reinforcements by default. Updated
`procedural-vs-principle.md` to mark this shipped.

**A — frontmatter schema.**
`schemas/article-frontmatter.schema.json` shipped (JSON Schema
2020-12). Required: `title`, `type`, `area`, `updated`, `status`.
Optional: `affects` (globs), `load_bearing` (bool), `references`
(list). Updated `frontmatter-as-source-of-truth.md` to reflect
shipped status.

**B — affects globs in drift-check.**
- Added `affects:` frontmatter to all five existing methodology
  articles (one of `dogfooding`, `frontmatter-as-source-of-truth`,
  `affects-globs`, `local-vs-pr-enforcement`,
  `procedural-vs-principle`).
- `drift_check.py` extended with `parse_frontmatter_affects` and
  `parse_articles_affects`. Hand-rolled YAML parser (no PyYAML dep
  to keep the Action runtime lean). Glob matcher upgraded with a
  custom `_glob_to_regex` that handles `**` recursion natively
  (previous fnmatch-only would have silently failed on nested files
  under `actions/drift-check/**`).
- `main()` now unions the frontmatter-derived mapping with the
  legacy CLAUDE.md table. Adopters can migrate incrementally.
- Smoke-tested against this repo's own `knowledge/`: 13 mapping rows
  derived from 5 articles' frontmatter; `**` matches nested files;
  exact-name matches still work.

Same-task new article: `concepts/tooling/drift-check.md` covers the
script's internals, the hand-parser limitations, the `**` matcher's
mapping table, and the dogfooding loop where the Action runs against
itself.

Articles updated, `index.md` updated with the new tooling row, this
log entry. No published prose touched.

## [2026-04-29] retrofit | knowledge base established + first 5 articles

This repo now dogfoods the methodology it defines. Brownfield retrofit
started today, triggered by an active development seam: the next-phase
methodology bundle (frontmatter schema + `affects:` globs + local
enforcement + procedural compliance).

Skeleton:

- `CLAUDE.md` at repo root — slim spine + same-task rule + procedural
  pre-commit checklist + red-flag phrases. Adopts the recommendations
  from `concepts/methodology/procedural-vs-principle.md` from day one.
- `knowledge/index.md`, `knowledge/log.md`.
- `concepts/methodology/`, `concepts/tooling/`, `connections/`.

First five articles, all under `concepts/methodology/`:

- `dogfooding.md` — why this repo applies its own methodology; what
  makes meta-repos different (articles document maintainer decisions,
  not adopter-facing examples).
- `frontmatter-as-source-of-truth.md` — proposed frontmatter schema
  with required + optional fields; rationale for moving article
  metadata from CLAUDE.md tables into the articles themselves.
- `affects-globs.md` — `affects: [globs]` in frontmatter as the
  canonical code↔article mapping; auto-generated table; backward-
  compatible upgrade path for the GH Action.
- `local-vs-pr-enforcement.md` — local CLI mirror of the drift check
  + pre-commit hook templates; failure modes each layer catches.
- `procedural-vs-principle.md` — same-task rule recast as a 6-step
  checklist; red-flag phrases as STOP signals; failure-mode framing.

These five capture the design decisions for the upcoming bundle. The
bundle implementation will land as separate commits, each touching the
relevant article(s) per the same-task rule.

Existing prose (`LIVING_DOCS_OVERVIEW.md`, the two adoption guides,
`GLOSSARY.md`, the templates, the Skill, the GH Action) is left
untouched per "document on touch, not on inventory." Each will get
articles when next modified.
