---
title: Paste-able prompts as methodology surface
type: concept
area: methodology
updated: 2026-04-29
status: thin
affects:
  - 'templates/prompts/**'
load_bearing: true
references:
  - concepts/methodology/frontmatter-as-source-of-truth.md
---

# Paste-able prompts

Some methodology steps are awkward as prose ("scan your codebase, pick three seams, write thin articles") but trivial as a Claude prompt. We ship the latter under `templates/prompts/`. Adopters paste them into Claude (Claude Code, claude.ai, any front end) at the moment the methodology calls for that workflow.

## Why ship them, vs. let adopters write their own

1. **They're load-bearing.** A prompt that lets Claude write articles without referencing the schema, the same-task rule, or the "thin is fine" principle produces work that quietly violates the methodology. Curated prompts encode those constraints.
2. **They're version-able.** Prompts evolve as the methodology evolves. Shipping them in the repo means changes get reviewed, articulated, and dated alongside the methodology decisions they encode.
3. **They reduce the bootstrap cliff.** Without a prompt, "write your first three articles" is the step where adopters stall. With a prompt, it's a paste-and-answer.

## What makes a good prompt for this methodology

- **Self-contained.** Adopters paste the prompt into a fresh Claude session that has no prior context. The prompt must itself link back to `LIVING_DOCS_OVERVIEW.md` and `CLAUDE.md` so Claude can read the methodology.
- **Constraint-stating.** Each prompt names the constraints that prevent common failure modes — speculative `affects:` globs in greenfield, back-fill past three articles in brownfield, API-doc rambling instead of decision capture. The constraints are *why* the prompt exists.
- **One screen.** ~80 lines. Long enough to encode the rules; short enough that the adopter scans before pasting.
- **Output-shaped.** Tells Claude exactly where files go, what frontmatter to use, what to do after writing (validate, log, suggest a commit, don't auto-commit).

## Drift risk

Prompts reference the frontmatter schema by path. Schema changes invalidate every prompt that reads it — that's why this article's `affects:` covers `templates/prompts/**`, and why `frontmatter-as-source-of-truth.md` should be reviewed for prompt impact whenever the schema changes. The drift-check enforces this through the same-task rule applied to either glob.

## What this article protects

If a future contributor proposes "let's just put the prompts inline in install.sh strings" — this article is the counterargument. Prompts are durable methodology artifacts; embedding them as shell-string-literals would lose review, versioning, and discoverability. They live as markdown files for the same reason articles do.

## Files

- `templates/prompts/first-articles-brownfield.md`
- `templates/prompts/first-articles-greenfield.md`
- `templates/prompts/README.md` — index and adopter instructions
