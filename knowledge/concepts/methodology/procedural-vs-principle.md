---
title: Procedural compliance — checklist, not principle
type: concept
area: methodology
updated: 2026-04-29
status: thin
---

# Procedural compliance

The same-task rule is a *principle*. Principles depend on the LLM
remembering them mid-task, which it doesn't reliably do. The rule has
to be expressed as a *procedure* (an explicit checklist) and reinforced
with concrete failure-mode framing and red-flag language.

## Observed failure mode

In the originating session (mira repo, 2026-04-28/29), the LLM
followed the same-task rule during the design phase (correctly created
articles when designing) but skipped it during implementation and test
commits. Five commits landed without article updates. The user had to
prompt: "is there anything to update?" before drift was caught.

Diagnosis: stating the rule once at the top of CLAUDE.md isn't
enough. The LLM read it at session start, internalized it as
background context, then context-switched into deep implementation
mode where the rule's surface-level reminder didn't fire.

## What works better

Three reinforcements, listed by impact:

### 1. An explicit pre-commit checklist

Replace "every change updates the matching article" (principle) with
a 6-step procedure (procedure):

```text
Before any commit:
1. List the files in this commit's diff.
2. For each: any article's `affects:` glob match it? Open those.
3. Did this change behaviour, config, models, structure, or a
   documented decision?
4. If yes: stage article update + log entry IN THIS SAME COMMIT.
5. If no article exists: write a thin one now. Don't defer.
6. If genuinely doc-irrelevant: commit body says
   "no knowledge impact: <reason>".
```

A checklist is harder to skip without noticing. Step 6 (forced
explicit acknowledgement of "no impact") is particularly load-
bearing — it converts an implicit skip into a conscious choice.

### 2. Red-flag phrases

Inner-monologue language signals impending rationalization. List
them explicitly:

- "I'll update docs after this commit lands."
- "The article is roughly correct."
- "This is too small to document."
- "Let me ship and circle back."
- "The reviewer can flag it if it matters."

Each = STOP and audit. Borrowed from the superpowers skill pattern,
which uses the same "if you think X, you're rationalizing" device
effectively.

### 3. Failure-mode framing

Compare:

- Principle: "Every change updates the matching article in the same
  task."
- Failure-mode: "Skipping the article update means it goes stale
  before the next read; the next session will trust the stale article
  and produce wrong work. The drift compounds."

The failure-mode version is harder to skip because it names the
concrete consequence. "Stale article ↦ wrong work ↦ compounding
drift" is a chain the LLM can re-derive on each attempted skip.

## Why all three together

Each reinforcement has a different leverage point:

- Checklist intercepts at the *commit* step (latest possible).
- Red flags intercept at the *thought* step (earliest possible).
- Failure framing intercepts at the *skip-rationalization* step
  (mid-stream).

Removing any one weakens the chain. The checklist alone could be
mechanically followed without internalizing why; red flags alone
require the LLM to be self-monitoring without a procedural anchor;
failure framing alone is the same principle dressed up.

## What lands in the templates

Both `templates/brownfield/CLAUDE.md` and
`templates/greenfield/CLAUDE.md` should ship with all three
reinforcements baked in by default. The repo's own CLAUDE.md (this
repo) does so as the working example.

The two adoption guides should also call out the procedural framing
in their methodology section, so adopters who customize CLAUDE.md
don't strip it out under the assumption that "the rule is enough."

## Files

- `CLAUDE.md` — this repo's working example
- `templates/{brownfield,greenfield}/CLAUDE.md` — to be updated to
  include the checklist + red flags + failure framing
- `LIVING_DOCS_OVERVIEW.md`, the two adoption guides — to be updated
  to mention procedural reinforcements when next touched
