# Bootstrap prompt — first 3 thin articles (brownfield)

> Paste the section below into Claude (Claude Code, claude.ai, or any
> Claude-powered tool) running in your project's root directory. Claude
> will scan your codebase, identify three seams worth documenting, and
> write the first three thin articles plus a `log.md` entry.

---

This repository just adopted the living-documentation methodology. Read these files first to understand the rules:

- `LIVING_DOCS_OVERVIEW.md` (or fetch from
  https://github.com/mpklu/living-doc/blob/main/LIVING_DOCS_OVERVIEW.md)
- `CLAUDE.md` (in this repo's root — the same-task rule applies to this work too)
- `schemas/article-frontmatter.schema.json` (the contract for article frontmatter)

## Your task

Write **exactly three** thin concept articles in `knowledge/concepts/`. Each ~150–250 words. The methodology is brownfield-not-back-fill — three is the cap, not the floor. Don't try to document everything.

## How to pick the three seams

Brownfield-adopting repos benefit most when the first articles cover *what's actively churning* or *what's hardest to onboard onto*. Choose by combining these signals:

1. **Hot-spot modules.** Run `git log --since="3 months ago" --pretty=format: --name-only | sort | uniq -c | sort -rn | head -20` (or scan recent commits manually). Modules that change a lot benefit most from a durable explanation of *why* they're shaped the way they are.
2. **Decision-dense areas.** Look for code with non-obvious structure — config layers, auth flows, data-pipeline boundaries, plugin systems. Anywhere a future contributor would need to ask "why was this done this way?"
3. **Onboarding pain points.** Anything mentioned in README/CLAUDE.md as "see X for details" but where X is thin or absent.

If unsure between candidates, ask me which to prioritize. Don't guess.

## What each article must contain

YAML frontmatter (validated against `schemas/article-frontmatter.schema.json`):

```yaml
---
title: <human-readable, ~6-10 words>
type: concept
area: <project-defined grouping, e.g. 'auth' or 'pipeline'>
updated: <today's date as YYYY-MM-DD>
status: thin
affects:
  - '<glob matching the code paths this article covers>'
load_bearing: true
---
```

Body:

- One paragraph: what this is and why it exists (the *purpose*, not the API surface).
- One section on the key decisions and their alternatives — what was ruled out, what made the chosen path right *here*.
- One section on what would invalidate this article (changes that should trigger a rewrite, not just an edit).
- Optional: a "Files" section pointing at the code, mirroring the `affects:` globs.

Place each article at `knowledge/concepts/{area}/{topic}.md`. Create the area subdirectory if it doesn't exist.

## Constraints — read before writing

- **Don't invent.** If you can't tell from the code why a decision was made, write what you *can* observe and ask me to fill in the rest. An imperfect-but-honest article beats a confident-but-wrong one.
- **Don't back-fill beyond three.** The methodology applies to changes from now on; the three articles are the *seed*, not exhaustive coverage.
- **No API documentation.** Articles capture decisions and reasoning. The code documents itself for "what does this function do." If you find yourself listing function signatures, stop.
- **Thin is fine.** ~200 words. The methodology values "capture first, refine second" — partial articles compound; missing articles don't.

## After writing

1. Append one entry to `knowledge/log.md` (newest at top) summarizing what you wrote, why those three seams, and any judgment calls you made.
2. Update `knowledge/index.md` so the new articles are reachable.
3. Run `scripts/validate-articles` (if present) to verify frontmatter — should print `✅ All N article(s) have valid frontmatter.`
4. Suggest a single commit: `git add -A && git commit -m 'living-docs: seed first 3 articles'` — but don't run it; let me review.

Then briefly summarize: which three seams you chose, why each, and any questions that came up.
